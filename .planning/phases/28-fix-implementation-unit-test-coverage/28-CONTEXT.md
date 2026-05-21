# Phase 28: Fix Implementation + Unit Test Coverage — Context

**Gathered:** 2026-05-21
**Status:** Ready for planning
**Source:** /gsd:discuss-phase 28 (Auto Mode — gray areas auto-resolved with recommended options; no AskUserQuestion prompts per harness Auto Mode)

<domain>
## Phase Boundary

Phase 28 delivers **the firmware-side fix for the Leonardo 64KB-read byte-jitter, plus a host-side Unity test that exercises the corrupting code path and fails on pre-fix code**. The fix lands as atomic commit(s) on `firestarter/v1.6-read-bug` (cut from `beta` at the start of this phase per Phase 27 D-03 deferral); each commit cites the Phase 27 RCA section in `.planning/v1.6-EVIDENCE.md` and the introducing-commit triangulation. Bench verification is Phase 29; Phase 28 is desk-side TDD only.

The RCA already pinpointed the corrupting code path with HIGH confidence — Phase 28 has a clean fix sketch + GATE-1.6 three-axis-green risk assessment to plan against:

1. **Primary mechanism (mandatory fix):** `firestarter/src/boards/leonardo_rurp_shield.cpp:rurp_set_data_input()` (lines 137-141) clears `DDRD` / `DDRC` / `DDRE` but leaves residual `PORTD` / `PORTC` / `PORTE` bits set from prior register strobes. Internal pullups bias 1-2 data pins HIGH against the chip's drive on partially-erased EPROM cells, producing single-bit XOR flips (78% of divergences). Fix: mirror Uno-side `df5fb44` (2026-05-13) — clear PORTx bits BEFORE clearing DDRx.
2. **Secondary mechanism (also recommended):** `rurp_read_data_buffer()` (lines 112-129) reads `PIND`, `PINC`, `PINE` in three separate machine instructions with no settling delay after the address-bus change driven by `rurp_set_address()`. Fix: insert `_NOP()` (or equivalent short stall) between PIN reads so the data bus stabilizes.

**In scope:**
- Cut `firestarter/v1.6-read-bug` branch from current `beta` tip (`bc0f5ac`, 1 docs-only commit ahead of tag `3.0.0b4`).
- Atomic fix commit(s) on `firestarter/v1.6-read-bug` editing ONLY `src/boards/leonardo_rurp_shield.cpp` — `rurp_set_data_input()` and `rurp_read_data_buffer()`. No other source files touched (read-path-only scope confirmed by Phase 27 GATE-1.6 analysis).
- Native Unity test under `firestarter/test/native/avr/test_data_input/` (or extend existing `test_dispatch/` layout) that mocks PORTx/DDRx/PINx via ArduinoFake + host stubs, sets PORTx to non-zero pre-state, calls `rurp_set_data_input()`, asserts PORTx data bits are cleared AND DDRx data bits are input. Test is committed BEFORE the fix (TDD red-bar evidence for FIX-02); demonstrated to FAIL on parent commit and PASS on fix commit.
- All three firmware envs (`uno`, `leonardo`, `uno328pb`) compile cleanly. Per-board `.hex` sizes recorded in fix commit message; drift > ±200 B flagged for re-review.
- `pio test -e native` stays green (existing `test_dispatch` + `test_messages` suites untouched + new `test_data_input` suite passes).
- Append `## Phase 28 — Fix Commit References` section to `.planning/v1.6-EVIDENCE.md` (matching the line-110 forward-annotation comment) with: firmware commit SHA(s), introducing-commit citation, Unity test file path + test name, per-board `.hex` sizes, and a Phase-29 bench-verification placeholder.
- GATE-1.6 desk-side confirmation: read-path-only edits, write path / VPP regulator / pulse-interval code paths untouched.

**Out of scope:**
- Bench validation / N≥5 byte-identity verification on the operator's hardware — Phase 29 owns this end-to-end (FIX-03's `firestarter write` + `dev read -s N` byte-comparison is bench-gated; "desk-side TDD-equivalent" per ROADMAP SC#3 means desk-side compile-clean + native Unity green + read-path-only code inspection).
- Documentation drift correction (Phase 27 EVIDENCE.md drift-correction table: `firestarter/CLAUDE.md` "1024-B" claims, `/workspaces/CLAUDE.md`, `26-02-SUMMARY.md:147`, `large-read-data-jitter-uno328pb.md:57`, EVIDENCE.md self-references) — Phase 30 milestone-close paperwork owns these per Phase 27 D-11.
- Reverting `firestarter/platformio.ini:64-65` Leonardo `DATA_BUFFER_SIZE` from `512` back to `1024` — the A/B test annotation stays; the buffer-size IS NOT the discriminator per Phase 27 H6 refutation, and keeping the FW identical except for the read-bug fix isolates the fix as the only variable for Phase 29's bench A/B.
- Host CLI cosmetic polish from Phase 26 follow-up (REVIEW WR-01 FAIL-without-divergence edge case, WR-02 `Board: unknown-board` field) — Phase 30 paperwork or post-v1.6.
- Host-side firestarter_app changes — RCA points entirely to firmware; the host-side `serial_comm.py` / `eprom_operations.py` path is clean (CRC8 + length-authoritative framing has zero failures in the bench logs).
- Plain Uno or uno328pb-silicon read-path changes — only Leonardo's `rurp_set_data_input` / `rurp_read_data_buffer` are corrupting (Plain Uno's df5fb44 fix already shipped 2026-05-13; uno328pb-silicon row deferred until reflash per `[[project_uno328pb_correction]]`).
- Moving the bug todo out of `pending/` — Phase 30 DOC-01 paperwork.
- Sub-repo `v1.6-read-bug` → `beta` merge — happens at the Phase 29 boundary to trigger a fresh pre-release cut for bench install (per ROADMAP §"Phase 28" SC#5).
- v1.1 FM1608 byte-0 carryover (separate hardware-level bug, separate debug session, `[[user_firestarter_repo_layout]]` shows it as the v1.1 80%-parked milestone — not in v1.6 scope).

</domain>

<decisions>
## Implementation Decisions

### Fix shape

- **D-01: Land BOTH RCA-named mechanisms as two atomic commits on `firestarter/v1.6-read-bug`.**
  Two separate atomic commits, each citing the specific RCA evidence axis it addresses:
  - **Commit 1 — `fix(leonardo): clear PORTD/PORTC/PORTE pullups in rurp_set_data_input` —** mirrors the Uno-side `df5fb44` pattern. Adds `PORTD = 0x00; PORTC &= ~PORTC_DATA_MASK; PORTE &= ~PORTE_DATA_MASK;` BEFORE the existing `DDRD &= ~PORTD_DATA_MASK;` / `DDRC &= ~PORTC_DATA_MASK;` / `DDRE &= ~PORTE_DATA_MASK;` lines. Addresses the 78%-single-bit-flip / address-bit-3-correlation evidence (the dominant corruption mechanism).
  - **Commit 2 — `fix(leonardo): add settling delay between PIND/PINC/PINE reads in rurp_read_data_buffer` —** inserts a short stall (`_NOP()` ×N, with N chosen so total stall ≥ ~125ns to cover one EPROM data-out propagation cycle at worst-case Vcc — researcher picks the exact instruction sequence) between the three `PINx` reads at lines 114-116. Addresses the multi-instruction-port-read timing race.
  Rationale:
  - **Both mechanisms are implicated by the binary evidence.** RCA explicitly says "the binary evidence implicates both the pullup-bias mechanism (via `rurp_set_data_input`) and the multi-register read timing (via the three-instruction PIND/PINC/PINE sequence in `rurp_read_data_buffer`)" (v1.6-EVIDENCE.md §"Fix sketch").
  - **Two atomic commits, not one squashed commit, because:** (1) each commit's "what this fixes" maps 1:1 to an RCA paragraph + evidence axis, so future readers can trace symptom → mechanism → fix; (2) `git bisect` between the two commits in Phase 29 (or post-ship) can answer the open question "is PORTx-clear alone sufficient or is the `_NOP()` settling needed?" — that experiment is cheaper to run with the commits split; (3) matches the v1.2 / v1.3 atomic-commit-per-RCA-axis pattern.
  - **Cost of "belt-and-suspenders" is trivial.** PORTx-clear adds ~6 instructions (~12 B flash); `_NOP()` adds 1-2 instructions per call site. Total expected drift ≤ 50 B per binary — deep in the noise vs the ±200 B ROADMAP SC#4 threshold.
  - **GATE-1.6 three-axis-green carries over** (Phase 27 §"GATE-1.6 Risk Assessment"). Both edits are in the READ path (`rurp_set_data_input` / `rurp_read_data_buffer`); the write path uses `rurp_write_data_buffer` + `rurp_set_data_output` (separate functions); VPP / regulator / pulse-interval code paths untouched. No mandatory mitigation items emerge.

  **Output the planner needs:** PLAN.md task list specifies the two commits, the exact line ranges, the diff shape (mirror of `df5fb44` for Commit 1; researcher picks `_NOP()` count for Commit 2 with rationale).

### Test approach

- **D-02: Single Unity native test suite under `firestarter/test/native/avr/test_data_input/`, exercising `rurp_set_data_input` post-conditions.**
  Use the existing `[env:native]` infrastructure documented in `firestarter/CLAUDE.md` §"Native (Host) Test Environment":
  - **Directory:** `firestarter/test/native/avr/test_data_input/` (parallel to existing `test_dispatch/` and `test_messages/`). Add `native/avr/test_data_input` to the `test_filter` allowlist in `platformio.ini` `[env:native]`.
  - **Files:**
    - `test_rurp_set_data_input.cpp` — Unity `RUN_TEST` cases covering Leonardo post-conditions.
    - `host_stubs.cpp` — extends `firestarter/test/native/avr/_shared/host_stubs_common.inc` if the new test references AVR symbols not already stubbed. The PORTx/DDRx/PINx registers are already host-mockable via ArduinoFake or simple `uint8_t` globals (existing pattern from `test_dispatch/`).
  - **Test shape:**
    1. **Pre-state setup:** set `PORTD`, `PORTC`, `PORTE` to non-zero values that simulate residual register state from prior `rurp_set_control_pins` / `rurp_write_data_buffer` strobes (e.g., `PORTD = 0xFF; PORTC = 0xFF; PORTE = 0xFF;`).
    2. **Action:** call `rurp_set_data_input()` (the Leonardo build path — guarded by `#ifdef ARDUINO_AVR_LEONARDO` in `leonardo_rurp_shield.cpp`; the native env needs `-D ARDUINO_AVR_LEONARDO` injected into the test build flags OR the function exposed via a board-agnostic shim — researcher picks the cleaner integration).
    3. **Post-condition assertions:**
       - `TEST_ASSERT_EQUAL_HEX8(0x00, PORTD & PORTD_DATA_MASK);` — data-bit pullups cleared
       - `TEST_ASSERT_EQUAL_HEX8(0x00, PORTC & PORTC_DATA_MASK);`
       - `TEST_ASSERT_EQUAL_HEX8(0x00, PORTE & PORTE_DATA_MASK);`
       - `TEST_ASSERT_EQUAL_HEX8(0x00, DDRD & PORTD_DATA_MASK);` — DDRx still set to input (regression guard)
       - `TEST_ASSERT_EQUAL_HEX8(0x00, DDRC & PORTC_DATA_MASK);`
       - `TEST_ASSERT_EQUAL_HEX8(0x00, DDRE & PORTE_DATA_MASK);`
  - **FIX-02 evidence requirement:** test is committed BEFORE the fix in Wave A. Wave A's executor confirms the test FAILS on the parent commit (i.e., red bar against `leonardo_rurp_shield.cpp` as it currently stands at `beta`). Wave B then lands the fix; the same test PASSES. The PR/commit narrative records both the parent-commit failure output and the fix-commit success output.
  - **`rurp_read_data_buffer` settling-delay coverage:** Unity cannot directly observe the physical `_NOP()` timing — that's a code-presence + regression check, not a behavioral test. Cover it as: (a) a presence check (`grep '_NOP'` in `leonardo_rurp_shield.cpp:rurp_read_data_buffer` as part of the Wave B verifier — narrative-level, not a Unity assertion), and (b) a Unity case that asserts `rurp_read_data_buffer()` returns the correct value given mock `PIND/PINC/PINE` (validates the shift-and-mask reassembly logic stays intact through the settling-delay edit; regression guard, not bug-evidence).

  **Test name (canonical):** `test_rurp_set_data_input_clears_data_pullups_leonardo` and `test_rurp_read_data_buffer_reassembles_data_bus`. Test file path: `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp`.

  Rationale:
  - **Existing infrastructure.** `[env:native]` + `unity` + `ArduinoFake` + the `test_dispatch/`/`test_messages/` allowlist pattern is already battle-tested through Phases 12, 17, 20. No new build system work — drop in a new directory, add one line to the `test_filter` allowlist, done.
  - **Phase-26 host-side pytest pattern mirrors this.** REPRO-03 shipped `test_consistency_check.py` (8 cases) under `firestarter_app/tests/` using the same pre-state-setup → action → post-condition shape. Phase 28's firmware Unity test is the firmware-side analog.
  - **Test asserts the FIX directly, not the symptom.** The 2.1% byte-jitter is a physical-bus race that requires real silicon to reproduce. Asserting the fix's *post-conditions* (PORTx cleared) is the host-testable mechanism — and is exactly what the Uno-side `df5fb44` would have caught if it had had a unit test (which it didn't; this is also a backfill for the Uno-side equivalent).

### Branch flow

- **D-03: Cut `firestarter/v1.6-read-bug` from `beta` HEAD (`bc0f5ac`) at the start of Wave A.**
  Cut point is current `beta` HEAD, which is 1 commit (`bc0f5ac docs(25): document uno328pb as third firmware build target (v1.5)`, docs-only) ahead of tag `3.0.0b4`. The docs commit is benign — no firmware semantics change between `3.0.0b4` and `beta` HEAD. Pinning to current `beta` HEAD avoids the awkward "branch off a tag that isn't `beta`'s HEAD" git operation.
  Rationale:
  - **Per Phase 27 D-03:** "If Wave B does not fire, the firmware branch is still deferred to Phase 28." Wave B did not fire (verdict `needs_bench: false`); Phase 28 cuts the branch.
  - **Per memory `[[feedback_branching]]`:** all v1.6 work lands on `v1.6-read-bug` branches in all 3 repos; sub-repos branch off `beta`. Compliant.
  - **Promotion gate:** `firestarter/v1.6-read-bug` → `beta` merge happens at the Phase 29 boundary to trigger a fresh pre-release cut (e.g., `3.0.0b5` or `3.0.1bN`) for bench install via `firestarter fw -i --pre --force`. NOT inside Phase 28 (per ROADMAP SC#5).
  - **Meta-repo coordination:** the meta-repo's `.planning/phases/28-*/` directory commits go on `main` (per the project's standing meta-repo convention — meta-repo never uses topic branches; the v1.6 work surface lives entirely on the sub-repos' `v1.6-read-bug` branches).
  - **firestarter_app sub-repo:** already on `v1.6-read-bug` (cut during Phase 26 for the diagnostic CLI work — commits `999c3cc` + `c057fe2` are visible). No new sub-repo branch needed for Phase 28; the host-side branch stays parked at its Phase 26 tip until Phase 30's potential host-side polish or directly to the Phase 29 promotion.

### Plan structure

- **D-04: Two-wave TDD plan — Wave A (failing test) + Wave B (fix + green).**
  - **Wave A — Plan 28-01 (autonomous: true, desk-side):** Cut `firestarter/v1.6-read-bug` from `beta` HEAD. Add new directory `firestarter/test/native/avr/test_data_input/` + Unity test files per D-02. Extend `platformio.ini` `[env:native].test_filter` to include the new suite. Execute `pio test -e native -f "*test_data_input*"` and capture the RED bar against the un-fixed `leonardo_rurp_shield.cpp`. Commit message: `test(leonardo): RED unity scaffold for rurp_set_data_input pullup clearing (FIX-02)`. Verifier confirms: (1) new suite shows FAIL with the expected post-condition assertion failures (not a build / link failure), (2) existing `test_dispatch` + `test_messages` suites still GREEN, (3) `pio run -e uno`, `-e leonardo`, `-e uno328pb` still build clean. Closes FIX-02's "test demonstrably fails on pre-fix code" half.
  - **Wave B — Plan 28-02 (autonomous: true, desk-side, depends on Wave A):** Apply the two atomic fix commits per D-01 to `leonardo_rurp_shield.cpp`. Re-run `pio test -e native -f "*test_data_input*"` and confirm GREEN. Re-build all three firmware envs (`pio run -e uno`, `-e leonardo`, `-e uno328pb`); capture per-board `.hex` sizes via `pio run --list-targets` / `wc -c .pio/build/*/firmware.hex` (or equivalent). Each fix commit message cites: (a) the RCA section in `.planning/v1.6-EVIDENCE.md` (full relative path + section header), (b) the introducing-commit triangulation (`5b1f1cd` for shape, "bug present at every tag from 2.0.2 through 3.0.0b4"), (c) the Wave A test file path + test name. Append `## Phase 28 — Fix Commit References` section to `.planning/v1.6-EVIDENCE.md` (recording firmware commit SHAs, test file, per-board sizes, Phase-29 bench placeholder). Closes FIX-01 + FIX-02's "PASS on post-fix code" half + ROADMAP SC#1/SC#2/SC#4 (commit-citation + Unity test + size record). FIX-03 is bench-gated and closes in Phase 29.

  Rationale:
  - **Matches v1.2/v1.3 atomic-commit-per-axis + Wave-0-scaffold-first pattern.** Phase 11 Plan 11-01 (RED scaffold first), Phase 12 Wave 0 (RED scaffold first), Phase 17 (same shape) — Wave A failing test → Wave B fix is the proven structure in this project.
  - **Each wave's atomic artifact is independently verifiable.** Wave A's RED bar is the evidence that FIX-02's "would fail on pre-fix code" half is satisfied (without Wave A, the FIX-02 claim is unfalsifiable). Wave B's GREEN bar + commit SHAs are the evidence for FIX-01.
  - **No bench escalation gate.** Unlike Phase 27 which had a conditional Wave B (`needs_bench: true/false`), Phase 28 is unconditionally desk-side. Phase 29 is the bench gate.

### Documentation drift correction

- **D-05: Defer all 5 drift-correction targets to Phase 30 milestone close.**
  The Phase 27 EVIDENCE.md drift-correction table lists 5 locations claiming "Leonardo 1024-B" (incorrect per `platformio.ini:64-65`):
  - `firestarter/CLAUDE.md` §"Architecture" / "Board differences"
  - `/workspaces/CLAUDE.md` §"Key Architecture Points"
  - `.planning/phases/26-cross-board-reproduction-diagnostic-tooling/26-02-SUMMARY.md:147`
  - `.planning/todos/pending/large-read-data-jitter-uno328pb.md:57` (hypothesis #4)
  - `.planning/v1.6-EVIDENCE.md:27` + `:54` (Phase 26 verdict text + entry conditions)
  Rationale:
  - **Phase 27 D-11 explicitly defers to Phase 28 polish OR Phase 30 cleanup.** Phase 28's center of gravity is fix + test; doc cleanup is paperwork. Phase 30 has DOC-01 / DOC-02 / MS-01 explicitly for milestone-close documentation work, plus the bug-todo move (DOC-01 already references the drift-correction context). Cleaner to bundle there.
  - **ROADMAP SC#1 for Phase 28 doesn't include doc edits.** It says fix commits cite RCA — it does not say correct historical drift in unrelated planning docs.
  - **One exception:** the `firestarter/platformio.ini:64-65` `; TEMP: 512` comment IS the source-of-truth and STAYS UNTOUCHED. Whether to revert Leonardo's `-D DATA_BUFFER_SIZE=512` back to `1024` is intentionally OUT OF Phase 28 scope (see `domain` "Out of scope" — Phase 29's bench A/B isolates the fix as the only variable).

### Introducing-commit citation format

- **D-06: Cite RCA + shape-introducing-commit in EVERY fix commit message.**
  Commit-message footer pattern (both Wave B commits):
  ```
  RCA: .planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Findings" (2026-05-21)
  Introducing-commit: 5b1f1cd "Leonardo is working, fast as a shark" (2025-02-11) — shape introduction
  Tag presence: bug present at every firmware tag from 2.0.2 through 3.0.0b4 (verified via tag-walk)
  Test: firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp
  ```
  Rationale:
  - **FIX-01 wants RCA citation + atomic commits.** This format satisfies it explicitly.
  - **RCA-03 milestone-bracket gets honored verbatim.** "Pre-v1.0" bracket + the `5b1f1cd` shape-introduction commit are exactly what RCA §"Introducing-commit triangulation (RCA-03)" produced; the fix commits cite both.
  - **Tag-walk reference closes the future-reader loop.** A maintainer 2 years from now opening `git log -- src/boards/leonardo_rurp_shield.cpp` can immediately reconstruct: "the function has had this shape since 2025-02-11; the bug shipped at every tag from 2.0.2 through 3.0.0b4; the fix is on `v1.6-read-bug`/post-3.0.0b4." No re-bisecting.

### Flash budget tracking

- **D-07: Record per-board `.hex` sizes in Wave B fix commit message; ±200 B threshold for re-review.**
  Expected drift per ROADMAP SC#4 baseline:
  - Leonardo (the tightest board): pre-fix ~85.4% flash utilization (v1.2 baseline). Post-fix expected delta: +12-50 B (PORTx-clear + `_NOP()` instructions). Well under ±200 B.
  - Uno: untouched (no edits to `uno_rurp_shield.cpp`). 0 B delta expected.
  - uno328pb: untouched. 0 B delta expected.
  Recorded as table in the Wave B commit message:
  ```
  Flash sizes (post-fix vs pre-fix beta@bc0f5ac):
  | Board     | Pre-fix .hex | Post-fix .hex | Δ      |
  |-----------|--------------|---------------|--------|
  | uno       | <N>          | <N>           | 0      |
  | leonardo  | <N>          | <N>+~40       | +~40   |
  | uno328pb  | <N>          | <N>           | 0      |
  ```
  Rationale: matches ROADMAP SC#4 verbatim; ±200 B is the auto-flag threshold; sizes go in EVIDENCE.md `## Phase 28 — Fix Commit References` for cross-phase visibility.

### EVIDENCE.md append section

- **D-08: Append `## Phase 28 — Fix Commit References` to `.planning/v1.6-EVIDENCE.md` at the end of Wave B.**
  Location anchor: line 110 `<!-- Phase 28 appends commit refs here: ## Phase 28 — Fix Commit References. -->`. Section body:
  - Commit SHA(s) + author + date + commit message subject for each fix commit.
  - Introducing-commit reference (per D-06).
  - Unity test file path + test name(s) + Wave A RED-bar SHA + Wave B GREEN-bar SHA.
  - Per-board `.hex` sizes table (per D-07).
  - Phase 29 placeholder: `<!-- Phase 29 appends post-fix bench verification: ## Phase 29 — Post-fix Consistency-Check Verification. -->` (already exists at line 111; do not duplicate).
  Rationale: same single-evidence-file-across-all-v1.6-phases pattern as Phase 27 D-04. One file for Phase 30 to archive.

### Reviewed Todos (cross_reference_todos)
None folded. The phase-28 scope is the firmware fix + unit test; the three pending todos that scored 0.6 are unrelated:
- `large-read-data-jitter-uno328pb.md` — the v1.6 bug itself; will be moved out of `pending/` by Phase 30 DOC-01 (not Phase 28).
- `avrdude-mcu-detection-fallback.md` — unrelated v1.5 carryover; deferred to its own milestone.
- `w27c512-eeprom-misclassification.md` — unrelated chip-DB classification issue; deferred to its own milestone.

### Claude's Discretion
- **Exact `_NOP()` count in Commit 2.** Researcher / planner picks N based on (a) the 32U4 datasheet's per-port-read propagation time and (b) the EPROM data-out worst-case access time at Vcc=4.5V. If unclear from docs, default to a single `_NOP()` between each PINx pair (2 `_NOP()`s total — minimum useful settling) with a comment citing the chosen rationale. Bench-confirmable in Phase 29.
- **Whether to expose `rurp_set_data_input` for native testing via `#ifdef ARDUINO_AVR_LEONARDO` extension OR via a board-agnostic shim.** Researcher picks the integration that requires the smallest delta to the existing native test build (likely: add `-D ARDUINO_AVR_LEONARDO` to the new `test_data_input` suite's local build flags so the `#ifdef ARDUINO_AVR_LEONARDO` guard in `leonardo_rurp_shield.cpp` fires under `[env:native]` for this one suite — same pattern used by `test_dispatch/` to selectively include `proms/*.cpp`).
- **Whether to add the second Unity case for `rurp_read_data_buffer` shift-and-mask reassembly.** Default: yes (regression guard against the settling-delay edit breaking the bit-mapping logic); but if it adds significant test scaffolding overhead, ship only the `rurp_set_data_input` case and rely on the existing physical-build evidence for the reassembly logic.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### RCA + bug evidence (primary inputs)
- `.planning/v1.6-EVIDENCE.md` §"Phase 27 — RCA Findings (2026-05-21)" — the 5-paragraph WHY + hypothesis-disposition table + introducing-commit triangulation + GATE-1.6 three-axis-green risk assessment + fix sketch + drift-correction targets. THE primary input for Phase 28.
- `.planning/v1.6-EVIDENCE.md` §"Fix sketch (Phase 28 handoff)" — names BOTH fix candidates (PORTx-clear in `rurp_set_data_input` + `_NOP()` settling in `rurp_read_data_buffer`); Phase 28 lands both per D-01.
- `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260521-134210/run_0[1-3].bin` — Phase 26 baseline binaries (3 × 64KB). Wave A's test can re-derive the 78% single-bit-flip + 63.2% address-bit-3 evidence via the 5-line Python cross-check at EVIDENCE.md lines 99-108 (sanity check only — not part of the Unity test).

### Phase 27 context (decisions Phase 28 inherits)
- `.planning/phases/27-root-cause-analysis/27-CONTEXT.md` — Phase 27 D-03 (deferred firmware-branch cut to Phase 28), D-04 (EVIDENCE.md append pattern), D-05 (DATA_BUFFER_SIZE=512 source-of-truth), D-06 (milestone-bracket-first introducing-commit strategy), D-11 (drift-correction targets → Phase 30).

### Roadmap + requirements (locked phase scope)
- `.planning/ROADMAP.md` §"Phase 28: Fix Implementation + Unit Test Coverage" (lines 72-83) — Goal + 5 success criteria + branch flow.
- `.planning/REQUIREMENTS.md` lines 24-26 — FIX-01, FIX-02, FIX-03 verbatim text. FIX-03 is bench-gated → Phase 29; Phase 28 closes FIX-01 + FIX-02.

### Sub-repo source-of-truth (Phase 28's edit target)
- `firestarter/src/boards/leonardo_rurp_shield.cpp` lines 112-129 (`rurp_read_data_buffer`) and 137-141 (`rurp_set_data_input`) — the two functions Phase 28 edits.
- `firestarter/src/boards/uno_rurp_shield.cpp` — `rurp_set_data_input` POST-`df5fb44` shape; the pattern Phase 28 mirrors for Leonardo. Commit `df5fb44` (2026-05-13) is the reference fix.
- `firestarter/include/rurp_shield.h` — PORTx/DDRx/PINx constant definitions; `PORTD_DATA_MASK` / `PORTC_DATA_MASK` / `PORTE_DATA_MASK` are defined inline at `leonardo_rurp_shield.cpp:16-18` (not in the header — researcher confirms scope at planning).
- `firestarter/platformio.ini` §`[env:native]` (lines 67-102) — test infrastructure (Unity + ArduinoFake + `test_filter` allowlist + `src_filter` rule). Phase 28 extends `test_filter` with one line.
- `firestarter/CLAUDE.md` §"Native (Host) Test Environment" — host-side Unity reuse pattern (`test/native/avr/<dirname>/`, `host_stubs.cpp`, `pgmspace.h` shim) and `pio test -e native -f` invocation. Phase 28 drops a new directory under this convention.

### Cross-cutting branching + memory
- Memory `[[feedback_branching]]` — all v1.6 work on `v1.6-read-bug` branches in all 3 repos; sub-repos branch off `beta`. Compliant with D-03.
- Memory `[[user_firestarter_repo_layout]]` — meta-repo at `/workspaces`, firmware sub-repo at `/workspaces/firestarter`, host sub-repo at `/workspaces/firestarter_app`.
- `.planning/PROJECT.md` §"Current Milestone: v1.6 Fix the Read Bug" lines 11-23 — milestone goal, target features, locked decisions (GATE-1.6, branch model, definition of done).

### Phase 26 host-side test pattern (precedent for D-02)
- `firestarter_app/tests/test_consistency_check.py` — 8-case pytest suite from REPRO-03. Host-side analog of the Unity test Phase 28 lands firmware-side. Same pre-state → action → post-condition shape.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **`firestarter/test/native/avr/` Unity infrastructure** (`platformio.ini` `[env:native]`, `host_stubs.cpp`, `_shared/host_stubs_common.inc`, `test/native/avr/test_dispatch/avr/pgmspace.h` host shim) — proven through Phases 12, 17, 20; reused as-is for Phase 28's new `test_data_input/` suite. One-line allowlist extension in `platformio.ini`.
- **`firestarter/src/boards/uno_rurp_shield.cpp:rurp_set_data_input()` post-`df5fb44`** — the EXACT pattern Phase 28 mirrors to Leonardo. Commit `df5fb44`'s diff (visible via `git show df5fb44 -- src/boards/uno_rurp_shield.cpp`) is the reference: clear PORTD before DDRD. The Leonardo equivalent needs PORTC + PORTE handling too (extra ports the Uno doesn't use for data) — straightforward generalization.
- **ArduinoFake mock library** (`fabiobatsilva/ArduinoFake@^0.4.0`, declared in `platformio.ini:89`) — already in dependency chain; provides host-side stubs for `_NOP()`, port-register access, etc.
- **`firestarter_app/tests/conftest.py` + `test_consistency_check.py`** — precedent for host-side fixture pattern; firmware Unity test is the analog (not literal reuse, but same shape).

### Established Patterns
- **TDD Wave 0 / Wave 1 split.** Phase 11 Plan 11-01 (RED scaffold) → Plan 11-02..06 (impl). Phase 12 Wave 0 → Waves 1-3. Phase 17 Wave 0 (RED) → Wave 1 (impl). Phase 28 follows the same — Wave A = RED scaffold; Wave B = fix + GREEN.
- **Atomic commit per RCA axis.** Phase 7 / Phase 8 / Phase 21 / Phase 23 all use the "one commit per logical unit, each with its own commit-message narrative" pattern. Phase 28's two fix commits follow this.
- **EVIDENCE.md append-only with forward-annotation comments.** `<!-- Phase N appends ... -->` HTML comments mark the insertion point for each downstream phase. Phase 28 honors the line-110 comment.
- **Tag-walk introducing-commit citation in commit message footer.** Phase 21 / Phase 22 / Phase 23 fix commits cite the introducing-commit + milestone bracket in a structured footer. Phase 28 follows the same format (D-06).
- **`#ifdef ARDUINO_AVR_LEONARDO` board-specific gating + `[env:native]` selective inclusion via `-D` flags.** `[env:native]` cross-compiles `src/proms/*.cpp` against host libc; board-specific TUs are excluded by `src_filter`. Phase 28's test_data_input suite needs `-D ARDUINO_AVR_LEONARDO` injected into ITS build flags to fire the Leonardo guard for this one suite (D-02 Claude's-discretion note).

### Integration Points
- **`firestarter/platformio.ini:78-80`** — `test_filter` allowlist. Phase 28 Wave A adds one line: `native/avr/test_data_input`. No other build-system changes.
- **`firestarter/test/native/avr/_shared/host_stubs_common.inc`** — shared stubs across native suites. Phase 28 extends ONLY if the new test references AVR symbols not already stubbed (PORTx/DDRx/PINx are bit-fields backed by `uint8_t` globals in the host build; should already be host-mockable).
- **`.planning/v1.6-EVIDENCE.md` line 110** — Phase 28's append point for the `## Phase 28 — Fix Commit References` section.
- **`.planning/v1.6-EVIDENCE.md` line 111** — Phase 29's reserved append point (untouched by Phase 28).

</code_context>

<specifics>
## Specific Ideas

- **The Uno `df5fb44` commit IS the reference fix-shape.** Phase 28 Commit 1 is "do the Leonardo version of this" — not "design a new fix from scratch." The diff visible at `git show df5fb44 -- src/boards/uno_rurp_shield.cpp` shows a 6-line addition (comment + `PORTD = 0x00;`) before the existing `DDRD = 0x00;`. Leonardo needs the 3-port equivalent (`PORTD`, `PORTC`, `PORTE` data bits).
- **Reuse the `df5fb44` commit-message narrative shape** — descriptive subject line, 2-paragraph body explaining the residual-pullup-bias mechanism, "Defensive — does NOT on its own fix [other symptoms]" disclaimer pattern (although in Phase 28's case, the RCA's HIGH-confidence verdict means the disclaimer flips to "this is THE root-cause fix").
- **Unity assertion macros to use:** `TEST_ASSERT_EQUAL_HEX8` (matches existing `test_dispatch/test_configure_memory.cpp` conventions — register-state assertions are hex-readable).
- **No `_BV()` macro avoidance.** `leonardo_rurp_shield.cpp:99-104` uses `_BV(N)` extensively for bit construction; Phase 28's edits keep the same convention.

</specifics>

<deferred>
## Deferred Ideas

- **Documentation drift correction** (5 locations claiming "Leonardo 1024-B") — Phase 30 DOC-01 / DOC-02 paperwork per D-05 and Phase 27 D-11.
- **`firestarter/platformio.ini:64-65` Leonardo `DATA_BUFFER_SIZE` revert from 512 → 1024** — intentionally NOT in Phase 28 per D-05 exception. If Phase 29 bench-confirms the read-bug fix at 512, that closes whether the A/B test annotation should be reverted as a follow-up; could land in Phase 30 polish or post-v1.6.
- **Host CLI cosmetic polish from Phase 26 REVIEW**: WR-01 FAIL-without-divergence edge case in `firestarter dev consistency-check`, WR-02 `Board: unknown-board` field. Phase 30 paperwork or post-v1.6.
- **Backfill Unity test for the Uno-side `df5fb44` fix.** Phase 28 lands the Leonardo-side test as a forward-looking artifact; the Uno-side fix (2026-05-13) shipped without a test. Could be added in Phase 30 or post-v1.6 as quality-debt cleanup, but no current bug rationale.
- **`firestarter info <chip>` crash** (`TypeError: '<=' not supported between instances of 'list' and 'int'` at `ic_layout.py:167`) — unrelated to v1.6 per Phase 26 EVIDENCE.md §"Scope changes". Out of milestone scope.
- **`0xda01` W27C512 chip-ID alias gap** — separate database issue per Phase 26 EVIDENCE.md §"Scope changes". Out of milestone scope.
- **uno328pb-silicon row in EVIDENCE.md** — deferred until operator reflashes the misidentified board per `[[project_uno328pb_correction]]`. Out of v1.6 scope.

### Reviewed Todos (not folded)
- **`large-read-data-jitter-uno328pb.md`** — the v1.6 milestone bug. Move out of `pending/` happens in Phase 30 DOC-01, NOT Phase 28. Phase 28 lands the fix that resolves the underlying bug; Phase 30 owns the todo-state transition + cross-references the Phase 27 RCA + Phase 28 fix commit SHAs.
- **`avrdude-mcu-detection-fallback.md`** — unrelated v1.5 carryover (operator labeled "low priority"). Deferred to its own milestone.
- **`w27c512-eeprom-misclassification.md`** — unrelated chip-DB classification issue (operator labeled "asap" but separate bug class). Deferred to its own milestone.

</deferred>

---

*Phase: 28-fix-implementation-unit-test-coverage*
*Context gathered: 2026-05-21*

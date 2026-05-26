# Milestones

## v1.6 — Fix the Read Bug (Shipped: 2026-05-26 — diagnostic + revert)

**Phases:** 5 (numbered 26-30) | **Plans:** 13 (Phase 26 = 2, Phase 27 = 3 including re-open Plan 27-05, Phase 28 = 4 including revert Plan 28-03 + parked Plan 28-04, Phase 29 = 4 including v2 re-iteration Plans 29-03/04, Phase 30 = 3) | **Timeline:** 2026-05-21 (planning start) → 2026-05-22 (Wave B FAIL — D-07 milestone-reopens) → 2026-05-26 (Phase 27 re-open Plan 27-05 closes + Phase 28 re-iterates with revert + Phase 29 v2 PASS_PARKED on bench + v1.7 ships in parallel + Phase 30 close) | **Ship tag:** `<TBD-from-30-03>` (default `3.0.0b5` — beta-only ship; operator may authorize `3.0.1` stable promotion in Plan 30-03 if appropriate) | **Commits:** meta-repo 48, firestarter sub-repo `<TBD-from-30-03>` (notable: `437339b6` reverted via `ea25174`; `4f205e58` `_NOP()` settling preserved), firestarter_app sub-repo `<TBD-from-30-03>` (notable: `999c3cc` host-CLI tip carrying the `dev consistency-check` GREEN implementation).

**Delivered:** v1.6 ships as a **course-correction milestone**. Per D-17v2 (re-scope locked 2026-05-26), the milestone delivers a permanent diagnostic + revert of the Phase 28 v1 firmware-induced regression — NOT a fix for the underlying 64KB streaming-read byte-jitter bug, which is intentionally deferred to v1.8 with characterized pattern findings as the RCA seed. Three artifacts ship to main: (1) `firestarter dev consistency-check <chip> --runs N` host CLI subcommand for N-run SHA-256 byte-identity measurement (REPRO-03, Phase 26), permanent regression check for any future fix candidate; (2) Phase 27 RCA narrative + Phase 27 re-open dual-cause disposition in `.planning/v1.6-EVIDENCE.md` (RCA-01..03); (3) Phase 28 v1's `437339b6` PORTx-clear cleanly reverted via `ea25174` in `firestarter/`, leaving Leonardo Modified Rev 0 returning to the Phase 26 baseline shape (WORST=0.047% zero-bytes across N=10 vs 83.8% pre-revert). The `4f205e58` `_NOP()` settling change is PRESERVED (Plan 28-04 parks permanently). Cross-board bench evidence and Bug A + Bug B pattern findings ship as the v1.8 RCA substrate. The original read-bug (Bug A = Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew; Bug B = Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch) is documented but not addressed.

### Key Accomplishments

1. **Phase 26 — Cross-board reproduction + diagnostic tooling (REPRO-01/02/03).** Landed `firestarter dev consistency-check <chip> --runs N` in `firestarter_app/firestarter/` — runs N consecutive `read` operations against a static chip, computes per-run SHA-256s, reports pass/fail verdict + first-divergence offset on mismatch + per-run binary capture under `.planning/v1.6/consistency-check-runs/<chip>-<board>-<timestamp>/`. 8-test pytest scaffold landed at `firestarter_app/tests/test_consistency_check.py`. Cross-board pre-fix baseline captured: Plain Uno (`/dev/ttyACM0`, Rev 2.0) = PASS (refuted the pre-existing-bug prediction); Leonardo (`/dev/ttyACM1`, Modified Rev 0) = FAIL (~2.1% jitter at 64KB; 1349/65536 divergent bytes). The diagnostic is the permanent post-fix regression check that v1.8 will invert.

2. **Phase 27 — RCA narrative + introducing-commit triangulation (RCA-01/02/03).** Identified the Leonardo data-bus pinout (PORTD/PORTC/PORTE three-port reassembly in `rurp_read_data_buffer`) + the missing PORTx-clear in `rurp_set_data_input` as the dual-mechanism source: residual pullup bias on partially-erased EPROM cells + multi-instruction PINx read race. 78% single-bit XOR distribution + 63% address-bit-3 correlation + 15% 0xFF partial-erased-chip signature triangulated H2 over H1/H3/H4/H5 with HIGH confidence (no Wave B instrumented bench build needed — Plan 27-02 parked). Introducing-commit bracketed to **pre-v1.0** via tag-walk of `2.0.2..3.0.0b4` (current shape introduced by `5b1f1cd` 2025-02-11). GATE-1.6 three-axis risk assessment GREEN.

3. **Phase 27 re-open (2026-05-26, Plan 27-05) — dual-cause disposition.** After Phase 29 v1 Wave B FAIL, Plan 27-05 confirmed dual-cause disposition: Outcome A (Leonardo firmware-induced via Phase 28 v1 `437339b6` PORTx-clear over-correction) + Outcome B-independent (uno328pb pre-existing hardware regression — independent of v1.6 scope; deferred to v1.8). The re-open closes with split-scope handoff: Leonardo revert via Plan 28-03; uno328pb operator hardware diagnosis deferred.

4. **Phase 28 — Initial fix + unit test (FIX-01/02/03 v1) shipped 2026-05-21 then reverted 2026-05-26.** Plan 28-01 RED Unity scaffold + Plan 28-02 two atomic fix commits (`437339b6` PORTx-clear masked-form mirror of Uno-side `df5fb44`; `4f205e58` `_NOP()` settling) landed clean desk-side with 22/22 Unity test PASS. Phase 29 v1 Wave B FAIL on Leonardo + uno328pb (83.8% zeros + 5 distinct SHAs) triggered D-07 milestone-reopens. **Plan 28-03 (2026-05-26)** atomically reverted `437339b6` alone via `ea25174` on `firestarter/v1.6-read-bug`; pullup-clear Unity test pruned as obsolete; Axis 4 `.hex` SHA identity table preserved (uno + uno328pb Δ=0). **Plan 28-04 (drafted-but-not-executed)** parks permanently — `4f205e58` `_NOP()` settling ships to main as the only behavioral firmware change from v1.6.

5. **Phase 29 v2 — operator-on-bench PASS_PARKED gate emission (2026-05-26).** Plan 29-03 desk-side rebuild from `firestarter/v1.6-read-bug` @ `efd203a` captured Leonardo SHA `734b9a85…` (68884 B) matching Phase 28 re-iteration Axis 4 expected. Plan 29-04 bench gate emission: 3× N=5 `firestarter dev consistency-check W27C512` (Modified Rev 0 canonical + Rev 2.0 bonus diagnostic + Modified Rev 0 replication). Modified Rev 0 WORST zero-byte ratio 0.047% (≤ 1.00% D-21v2 structured_data threshold); 99.50% cross-session-stable-byte agreement; Phase 26 baseline shape match. Emitted `plan_28_04_gate: pass_parked` per D-22v2. VERIFY-02 PASS; VERIFY-01 + VERIFY-04 unconditionally DEFERRED to v1.8 per D-29v2 + D-30v2; VERIFY-03 DEFERRED per D-26v2 operator-optional. Pattern findings (Bug A + Bug B) characterized in `.planning/v1.6-EVIDENCE.md` H3 block as v1.8 RCA seed.

6. **Phase 30 — Documentation + milestone close (DOC-01/02 + MS-01).** Read-bug todo `large-read-data-jitter-uno328pb.md` moved from `.planning/todos/pending/` to `.planning/todos/pending/v1.8-seed/` with `status: v1.8-deferred` + Bug A + Bug B annotation header + 15 N=5 W27C512 binaries + Phase 29 v2 H3 block + Plan 29-04 SUMMARY cross-references (DOC-01). PROJECT.md flipped to ship-state reflecting the re-scoped "diagnostic + revert" disposition; v1.7 shipped-archive entry written; Current Milestone block flipped per operator discretion (default: v1.8 PROPOSED). v1.5 backlog carry-forward annotated `carried forward to v1.8 with Bug A + Bug B pattern findings` (DOC-02). MILESTONES.md grows this entry (MS-01). Phase artifacts archived via `.planning/v1.6-archive.sh` in Plan 30-02; sub-repo branch promotion in Plan 30-03 (operator-authorized).

### Branch Strategy

Per operator standing instruction (memory `feedback_branching`): all v1.6 work landed on `v1.6-read-bug` branches in all 3 repos. Sub-repos branched off `beta@3.0.0b4` post-v1.5 ship; meta-repo `v1.6-read-bug` branched off `main`. Plan 30-03 (operator-authorized, NOT autonomous) handles the sub-repo `v1.6-read-bug` → `beta` merge + meta-repo `v1.6-read-bug` → `main` merge. **Per the re-scope (D-17v2): this is likely a BETA-ONLY ship — the read-bug is not fixed, so stable promotion is operator-discretion.** Default suggestion: cut `3.0.0b5` pre-release from `beta` carrying the `4f205e58` `_NOP()` settling only; defer `3.0.1` stable bump until v1.8 ships the real read-bug fix.

### Open backlog carried forward to v1.8

The Phase 29 v2 pattern analysis (15 N=5 W27C512 binaries) surfaced two independent failure modes that DO NOT close in v1.6 — they carry to v1.8 as the RCA starting hypothesis substrate:

- **Bug A — Modified Rev 0 upper-address jitter (the original v1.6 read-bug; carries to v1.8).** 858/65536 (1.31%) byte positions disagree within N=5; A15=1 → 1.70% jitter vs A15=0 → 0.92% (1.86× skew); 63% of jitters BIT-RAISE; mean delta +8.89. Hypothesis: upper-address signal-integrity (A14/A15 high → ground bounce / capacitive crosstalk) + weak data-bus pull-down. `_NOP()` settling at `4f205e58` targeted timing but is insufficient on its own.
- **Bug B — Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch (independent shield-specific issue).** All 5 Rev 2.0 N=5 byte-identical (zero within-session jitter); 49.06% of bytes are bus-tristate symptoms (36.19% `0xff` + 12.87% `0x00`); VPP=13.1-13.2V > 12.0V expected; 83.1% bytes differ from Modified Rev 0 with uniform XOR across D0-D7 (NOT a single stuck data line).
- **VERIFY-01 (uno328pb byte-identity)** — DEFERRED to v1.8 per D-29v2 (independent pre-existing hardware regression per memory `project_uno328pb_bench_instability_27_04`).
- **VERIFY-03 (1KB low-rate jitter)** — DEFERRED operator-optional per D-26v2 (over-determined by 64KB structured_data verdict via shared `_run_state_machine` + `_main_phase_read_data` code path).
- **VERIFY-04 (Phase 24 BENCH-02 closure)** — DEFERRED to v1.8 per D-30v2 (BENCH-02 needs working read path which carries to v1.8 alongside Bug A fix).
- **`w27c512-eeprom-misclassification.md`** (HIGH, operator-tagged "asap") — still carried forward; out-of-scope of v1.6 per D-17v2.
- **`avrdude-mcu-detection-fallback.md`** (low) — still carried forward.

v1.8 RCA substrate (ready to consume): `.planning/v1.6/consistency-check-runs/W27C512-leonardo-20260526-*-v2*/` (15 N=5 W27C512 binaries — Modified Rev 0 canonical + Rev 2.0 bonus + Modified Rev 0 replication); `.planning/v1.6-EVIDENCE.md` Phase 29 v2 H3 block; `.planning/phases/29-multi-board-bench-verification/29-04-SUMMARY.md` canonical close narrative; v1.7 substrate (`.planning/v1.7-SHIELD-REVS.md` per-rev capability table + labeled schematic + shield-version-detect firmware plumbing — enables v1.8 to design A/B fix candidates knowing exactly which silkscreen rev sits on the bench at each step).

### Stats

| Metric | Value |
|--------|-------|
| Phases | 5 (numbered 26-30) |
| Plans | 13 (Phase 26 = 2, Phase 27 = 3 incl. re-open 27-05, Phase 28 = 4 incl. revert 28-03 + parked 28-04, Phase 29 = 4 incl. v2 re-iteration 29-03/04, Phase 30 = 3) |
| Requirements (v1.6 scope) | 16 total; closed-as-DELIVERED: REPRO-01/02/03 + RCA-01/02/03 + FIX-01/02/03 + DOC-01/02 + MS-01 (12); closed-as-DEFERRED-to-v1.8: VERIFY-01 + VERIFY-03 + VERIFY-04 (3); closed-as-PASS via structured_data shape: VERIFY-02 (1) |
| Meta-repo commits | 48 (`git log --oneline --since=2026-05-21 -- .planning/ \| wc -l` at Phase 30 Plan 30-01 write time, pre-30-01 commits) |
| Firmware sub-repo commits | `<TBD-from-30-03>` (notable: `437339b6` reverted via `ea25174`; `4f205e58` `_NOP()` settling preserved; HEAD at close = `efd203a` per Phase 29 v2 VERIFICATION) |
| Host sub-repo commits | `<TBD-from-30-03>` (notable: `999c3cc` carries the `dev consistency-check` GREEN implementation + 8-test pytest scaffold) |
| Bench sessions (operator-on-bench) | 4 (Phase 26 Wave B, Phase 29 v1 Wave B Attempt 1, Phase 29 v1 Wave B Attempt 2 FAIL, Phase 29 v2 Wave B PASS_PARKED) |
| Bench binaries captured | 21 × 65536 B (6 in Phase 26 baseline + 15 in Phase 29 v2 across 3 sessions) + 3 Phase 29 v1 sessions (audit-trail-immutable per D-25v2) |
| New CLI subcommand | 1 (`firestarter dev consistency-check`) |
| New pytest tests | 8 (`firestarter_app/tests/test_consistency_check.py`) |
| New Unity tests (firmware) | 2 (`test_rurp_set_data_input_clears_data_pullups_leonardo` + `test_rurp_read_data_buffer_reassembles_data_bus`; pullup-clear pruned in Plan 28-03) |
| Hardware impact | Leonardo `.hex` size unchanged from `beta@3.0.0b4` (PORTx-clear reverted); `4f205e58` `_NOP()` settling adds ~4 B (well within ±200 B GATE-1.6); Uno + uno328pb Δ=0. The only behavioral firmware ship is the `_NOP()` settling; the read-bug is NOT fixed by design per D-17v2. |

### Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| **D-17v2 (re-scope 2026-05-26): v1.6 ships as "diagnostic + revert" NOT as "fix the read-bug"** | Phase 29 v1 Wave B FAIL revealed Phase 28 v1 firmware-induced regression on Leonardo (83.8% zeros). Plan 27-05 re-open confirmed dual-cause disposition (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb hardware). Continuing with a wrong fix would compound technical debt; clean revert + characterized pattern findings as v1.8 RCA seed is the integrity-preserving path. | ✓ Good (Phase 29 v2 PASS_PARKED confirms Leonardo Modified Rev 0 returns to Phase 26 baseline shape; Bug A + Bug B characterized; v1.7 substrate shipped in parallel gives v1.8 known-good schematics) |
| **D-22v2: triple-state Plan 28-04 gate emission (`pass_parked` \| `activate` \| `needs_human`) APPENDED to verdict file** | Preserves the audit trail of the default-before-bench state alongside the live emission; avoids overwriting prior decisions; mirrors v1.4's E2E iterative substrate fix pattern. | ✓ Good (Phase 29 v2 emitted `pass_parked`; verdict file 8-line preamble byte-identical pre/post; D-25v2 immutability satisfied) |
| **D-25v2: Phase 29 v1 audit-trail content byte-identical post-v2** | Re-iteration must not overwrite prior failure evidence — the FAIL outcome is itself load-bearing evidence (it triggered Plan 27-05 + Plan 28-03). Immutability rule with single explicit D-24v2 exception (placeholder cross-link replacement). | ✓ Good (lines 188-376 SHA-256 byte-identical across `f902a63` and `47c364c`; verified in Phase 29 VERIFICATION.md) |
| **D-29v2: VERIFY-01 (uno328pb byte-identity) DEFERRED to v1.8 unconditionally** | uno328pb regression is independent pre-existing hardware issue per memory `project_uno328pb_bench_instability_27_04` + Plan 27-04 falsifier `d9e51b7e…` over-determination; not a v1.6 scope item. v1.7 labeled-schematic + shield-version-detect substrate gives v1.8 the foundation. | ✓ Good (Phase 29 v2 closes VERIFY-01 as DEFERRED; not an artificial failure) |
| **D-30v2: VERIFY-04 (Phase 24 BENCH-02 closure) DEFERRED to v1.8 unconditionally** | BENCH-02 needs working read path — carries to v1.8 alongside Bug A fix. Write-path non-regression already confirmed desk-side via Phase 28 re-iteration Axis 4 `.hex` SHA identity (uno + uno328pb Δ=0). | ✓ Good (BENCH-02 carry is explicit, not silent; v1.8 inherits the substrate cleanly) |
| **D-27v2: Modified Rev 0 + voltage-divider mod is the canonical bench shield for Phase 29 v2** | Anchors against Phase 26 baseline (same shield); Rev 2.0 bonus diagnostic produces additive forward-traceability for v1.8 but does NOT replace the canonical anchor. | ✓ Good (multi-shield bench session within single operator visit per `feedback_chip_out_before_sideload` discipline; produced richer pattern findings without weakening gate verdict) |
| **D-21v2: structured_data shape classification threshold = zero-byte ratio < 1.00% across N=5** | Distinguishes "Leonardo baseline jitter character per Phase 26" from "Phase 28 v1 firmware-induced zeros-dominant regression" empirically. | ✓ Good (Phase 29 v2 WORST 0.047% across N=10; well-clear of threshold; classification is unambiguous) |
| Phase 30 SC#5 sub-repo branch promotion = operator-authorized, NOT autonomous (default beta-only) | Per memory `feedback_branching` + the re-scope (read-bug not fixed, stable bump is premature). Plan 30-03 documents exact `git` commands + branch identity verification but does not pre-decide ship tag. | Pending (Plan 30-03 — operator confirms `3.0.0b5` beta-only vs `3.0.1` stable promotion at execution time) |

### Known Gaps (deferred to v1.8 — pointers to v1.8 RCA seed substrate)

Per D-17v2 re-scope, the following are explicit pointers to v1.8 RCA hand-off material recorded in `.planning/todos/pending/v1.8-seed/large-read-data-jitter-uno328pb.md` + `.planning/v1.6-EVIDENCE.md` Phase 29 v2 H3 block + `.planning/phases/29-multi-board-bench-verification/29-04-SUMMARY.md`:

- **Bug A (Modified Rev 0 upper-address jitter)** — the original v1.6 read-bug; carries to v1.8 with characterized address-bit correlation (A15=1 → 1.86× skew; A14=1 → 1.46× skew) + bit-direction bias (63% BIT-RAISE) + upper-24KB-dominant footprint. v1.7's per-rev capability matrix anchors which shield is on the bench at each v1.8 fix-candidate A/B step.
- **Bug B (Rev 2.0 /CE-or-/OE timing + voltage-divider mismatch)** — independent shield-specific issue; carries to v1.8 with VPP=13.1V anomaly + 49.06% bus-tristate-symptom signature + uniform D0-D7 XOR distribution.
- **VERIFY-01 (uno328pb byte-identity)** — DEFERRED to v1.8; independent pre-existing hardware regression.
- **VERIFY-03 (1KB low-rate jitter)** — DEFERRED operator-optional; over-determined by 64KB structured_data verdict.
- **VERIFY-04 (Phase 24 BENCH-02 closure)** — DEFERRED to v1.8; needs working read path.
- **`w27c512-eeprom-misclassification.md`** (HIGH) — still carried forward; v1.6 out-of-scope per D-17v2.
- **`avrdude-mcu-detection-fallback.md`** (low) — still carried forward.

### Hardware impact

The only behavioral firmware change shipping from v1.6 is the `_NOP()` settling at commit `4f205e58` in `firestarter/src/boards/leonardo_rurp_shield.cpp:rurp_read_data_buffer` (adds 2 `_NOP()` calls between PIND/PINC/PINE reads — ~125 ns settling, comfortably > 90 ns W27C512 tACC; ~8 ms total overhead per 64KB read, invisible against ~3 s read time). Phase 28 v1's PORTx-clear at `437339b6` was reverted via `ea25174` and DOES NOT ship. Uno + uno328pb `.hex` artifacts byte-identical to `beta@3.0.0b4` (Δ=0). Leonardo `.hex` carries the `_NOP()` settling only (well within ±200 B GATE-1.6 budget). The 64KB streaming-read byte-jitter bug itself is NOT fixed and remains by design per D-17v2 re-scope — characterized as Bug A + Bug B in the v1.8 RCA seed substrate.

---

## v1.5 — Arduino Uno (ATmega328PB) Board Support (Shipped: 2026-05-21)

**Phases:** 5 (numbered 21-25) | **Plans:** 6 (Phase 21 = 2, Phase 22 = 1, Phase 23 = 2, Phase 24 = bench-only / 0 plans, Phase 25 = 1) | **Timeline:** 2026-05-20 (planning) → 2026-05-21 (execution + bench validation + close — single-day operator-on-bench cut) | **Ship tag:** 3.0.0b4 (auto-incremented from v1.4's 3.0.0b3 via the v1.4 lockstep mechanism on push to `beta`) | **Commits:** meta-repo ~30, firestarter sub-repo 3 (`da607d4` + `ab7c2a9` + merge `62df517`), firestarter_app sub-repo 4 (`67c8357` + `d13d9b1` + `c184910` urclock fix + merge `75db46e`)

**Delivered:** Added `uno328pb` as a third first-class firmware target alongside `uno` and `leonardo`. Three-board release matrix flows end-to-end: `pio run` emits three `.hex` files per cut → CI workflows' existing `files: .pio/build/**/firestarter_*.hex` glob picks up the new artifact with zero workflow YAML changes → `firestarter fw -i --pre` resolves and flashes the matching artifact for `uno328pb`-reporting devices. Bench-validated on operator's 328PB-Uno (/dev/ttyUSB0): full install path proven on real silicon, post-flash handshake reports `v3.0.0b4, controller: uno328pb`. Existing `uno` + `leonardo` artifacts remain byte-identical (GATE-1.5 preserved via `cmp -s` against baselines captured at firestarter/beta @ 5fd751e).

### Key Accomplishments

1. **Firmware build target (Phase 21 — FW-01..FW-04).** New `[env:uno328pb]` in `firestarter/platformio.ini` between `[env:uno]` and `[env:leonardo]` (`platform = atmelavr`, `board = ATmega328PB`, `-D RURP_BOARD_NAME=\"uno328pb\"`). MiniCore-the-core is bundled inside `platformio/atmelavr@5.2.0` via the stock `ATmega328PB` board file's `build.core` field — no custom board JSON needed (CONTEXT D-05 Path B). Atomic 4-site macro-guard widening (`ARDUINO_AVR_UNO` → `defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)`) in `uno_rurp_shield.cpp`, `rurp_common.cpp` (×2 lines), `rurp_register_utils.h` — no umbrella macro per CONTEXT D-02. `name_firmware.py` reworked to derive PROGNAME from `-D RURP_BOARD_NAME` via `env.ParseFlags()` so the board-id triple (board-id = artifact-name = handshake-string) has a single source of truth.

2. **Release pipeline (Phase 22 — REL-01, REL-02).** `platformio.ini` `default_envs` widened to `uno, uno328pb, leonardo` (Phase 21 D-08 section order); ROADMAP SC#1 literal realigned to match (Phase 21 D-12 hand-off). Zero `.github/workflows/*.yml` edits — both `build.yml:105` and `beta-build.yml:92` already used the `firestarter_*.hex` glob. Verified by `softprops/action-gh-release@v2` attaching the third asset on the first real beta cut.

3. **Host CLI installer (Phase 23 — INST-01, INST-02, INST-03, GATE-01).** Two-file edit in `firestarter_app/`: `firmware.py:_install_with_avrdude` gained `uno328pb` elif branch with `("atmega328pb", "urclock", 115200)` profile (bench-validated; initial guess of `arduino` programmer_id was incorrect — operator's MiniCore-flashed 328PB-Uno ships with Urclock bootloader); `main.py` argparse `-b/--board` `choices=` widened to `["uno", "uno328pb", "leonardo"]`. TDD shape (RED tests landed first; 5 new test methods in `test_firmware_install.py` plus a `_FakeAvrdude` module-local mock helper). Full pytest 82/82 PASS; GATE-01 `pytest -k "not uno328pb"` = 77 PASS byte-identical to pre-Phase-23.

4. **Bench validation (Phase 24 — BENCH-01, BENCH-02).** Merge `v1.5-uno328pb` → `firestarter/beta` triggered CI → GitHub Pre-release `3.0.0b4` with three `.hex` artifacts. `firestarter fw -i --pre --force` on `/dev/ttyUSB0` against the 328PB-Uno + RURP shield: downloaded `firestarter_uno328pb.hex` (22,340 bytes in 0.51s), flashed via avrdude+urclock (5.94s), post-flash handshake reports `version: 3.0.0b4, controller: uno328pb`. VPP 12.4–12.5V stable, VPE 14.4V stable, hardware rev EEPROM-read works. Write path bench-validated for small (16B) and medium (256B) writes via SST27SF512 in socket — every committed bit matches expected `pre AND target` pattern byte-for-byte. Full evidence in `.planning/v1.5-BENCH-RESULTS.md`.

5. **Documentation + milestone close (Phase 25 — DOC-01, DOC-02, MS-01).** Both READMEs (firmware + host CLI) gained three-board references and a per-board PlatformIO env table; ROADMAP Phase 21–24 closed with shipped dates; REQUIREMENTS FW-01..04 + REL-01..02 + INST-01..03 + GATE-01 + BENCH-01..02 all flipped to `[x]`. PROJECT.md updated to "v1.5 shipped 2026-05-21".

### Branch Strategy

Per operator standing instruction (memory `feedback-branching-firestarter-milestones`): all milestone work landed on `v1.5-uno328pb` branches in all 3 repos (meta + firestarter + firestarter_app). Sub-repos merged `v1.5-uno328pb` → `beta` during Phase 24 to trigger the beta CI cut. Meta-repo `v1.5-uno328pb` retains the full planning trail and gets merged to `main` at milestone-close (this file).

### Open backlog carried v1.5 → v1.6 → v1.8

The Phase 24 bench rigor surfaced three pre-existing bugs that do NOT block v1.5 ship but warrant near-term attention:

- **`large-read-data-jitter-uno328pb.md`** (HIGH, **affects all controllers**) — full 64KB streaming reads return ~57% different bytes across consecutive reads. 3-shield A/B/C triage proves the bug is hardware-independent and existed in v1.4 unnoticed. **Carried forward to v1.8** with characterized Bug A (Modified Rev 0 upper-address jitter, A15=1 → 1.86× skew) + Bug B (Rev 2.0 /CE-or-/OE timing + VPP=13.1V) pattern findings per Phase 29 v2 close (NOT resolved in v1.6 — see v1.6 entry below for D-17v2 re-scope rationale).
- **`w27c512-eeprom-misclassification.md`** (HIGH, operator-tagged "asap") — chip database routes 8 electrically-erasable EEPROMs (W27C512, W27E512, W27C257, W27E257, SST27SF512, SST27VF512, SST27SF256, SST27VF256) to the UV-only EPROM dispatch path. `firestarter erase <chip>` returns `ERROR: Not supported`. Fix requires new firmware dispatch for "12V VPP write + electrical erase" chips, not a one-line override. **Still carried forward** — not in scope for v1.6 (per D-17v2 re-scope, v1.6 ships as 'diagnostic + revert' only).
- **`avrdude-mcu-detection-fallback.md`** (low) — host CLI enhancement for blank-chip recovery; empirical basis bench-validated (avrdude reveals MCU type via stderr on signature mismatch). **Still carried forward** — not in scope for v1.6 (per D-17v2 re-scope, v1.6 ships as 'diagnostic + revert' only).

### Key Decisions (locked)

- **Path B for FW-02** (CONTEXT D-05): drop `boards/uno328pb.json`; use stock `platform = atmelavr` + `board = ATmega328PB`; rework `name_firmware.py` to derive PROGNAME from `RURP_BOARD_NAME`. Preserves the locked board-id-triple invariant.
- **`platform = atmelavr`** (RESEARCH Open Q1 resolution): `MCUdude/MiniCore` is not a registered PlatformIO platform; the MiniCore core ships bundled inside atmelavr@5.2.0.
- **`programmer_id="urclock"`** for uno328pb (bench-validated): MiniCore's stock bootloader on the operator's 328PB-Uno is Urclock, not optiboot. Phase 23 CONTEXT D-02 documented this as a known contingency; bench confirmed it 2026-05-21.
- **GATE-1.5 byte-identity** (CONTEXT D-04): `firestarter_uno.hex` + `firestarter_leonardo.hex` from v1.5 cuts byte-identical to pre-v1.5 (modulo `update_version.py` drift). Baselines captured at `firestarter/beta` tip `5fd751e` (SHA-256 `0dd5c01a…` uno, `f49e2a57…` leonardo); verified via `cmp -s` during Phase 22.
- **Local milestone branches, beta-cut only on operator authorization** (memory `feedback-branching-firestarter-milestones`): work stays on `v1.5-uno328pb` until the operator explicitly authorizes a merge to `beta`. The "merge in to beta and test that we can install via the app to the pb" instruction on 2026-05-21 was the explicit auth point.

---

## v1.4 — Beta & Pre-release Deployment Pipeline (Shipped: 2026-05-20)

**Phases:** 6 (numbered 15-20) | **Plans:** 10 (Phase 15 = 4, Phase 16 = 1, Phase 17 = 1, Phase 18 = 2, Phase 19 = 1, Phase 20 = 1) | **Timeline:** 2026-05-20 (single-day cut: planning + execution + live verification including real-hardware flash) | **Ship tag:** 3.0.0b3 (auto-incremented from b1/b2 during E2E iteration; .pyc hygiene fix triggered b3) | **Commits:** meta-repo 56, firestarter sub-repo 13, firestarter_app sub-repo 17

**Delivered:** Added a parallel beta / pre-release deployment channel across both Firestarter sub-repos without touching the existing main → stable pipelines. Branch-driven trigger (`beta` branch in each sub-repo) wired to new beta workflows that emit PEP 440 / matching pre-release version strings, publish PyPI pre-release wheels (installable via `pip install --pre`), and create GitHub Pre-releases with `make_latest: false` carrying per-board `firestarter_*.hex` artifacts. App and firmware ship locked-step on a single `BETA_VERSION` operator input. Beta-installed app grows three new CLI flags (`--pre`, `--firmware-version`, `firmware list`) plus a PEP 440-safe version comparator; stable-installed app's `firestarter --install` defaults remain byte-identical to pre-v1.4. Documentation: both READMEs grew a Beta channel section; meta-repo `v1.4-RELEASE-PROCEDURES.md` documents the release-engineer cutting workflow.

### Key Accomplishments

1. **Versioning + lockstep foundation (Phase 15 — VER-01/02/03).** Extended both
   sub-repos' `.github/scripts/update_version.py` to recognize beta-branch context
   and emit PEP 440 pre-release identifiers (`X.Y.ZbN`, `X.Y.ZrcN`) on `BETA_VERSION`
   input, preserving stable-branch patch-bump behavior verbatim. Shared validation
   regex `^[0-9]+\.[0-9]+\.[0-9]+(b|rc)[0-9]+$` between both scripts (string-equality
   lockstep check). Lockstep mechanism finalized as **manually-paired beta-branch
   push with explicit `BETA_VERSION` input** (rejected: shared meta-repo VERSION file,
   cross-repo `repository_dispatch`). Documented in `15-LOCKSTEP-PROCEDURE.md` and
   proven via `lockstep-dryrun-fixture.sh` cross-script byte-identity check.

2. **App beta release pipeline (Phase 16 — REL-01, GATE-01).** New
   `firestarter_app/.github/workflows/beta-release.yml` — single-file deliverable
   covering push:beta + workflow_dispatch triggers, inline CI gates (pytest),
   Phase 15 version-bump call, GitHub Pre-release creation, and PyPI publish via
   the existing `publish.yml`. GATE-01 preserved: stable `main`-push behavior
   byte-identical to pre-v1.4.

3. **Firmware beta release pipeline (Phase 17 — REL-02, GATE-02).** New
   `firestarter/.github/workflows/beta-build.yml` — single-file deliverable
   covering push:beta + workflow_dispatch triggers, inline catalog/codegen/Unity/
   PlatformIO gates, Phase 15 version-bump auto-commit, `pio run` build, and
   GitHub Pre-release with `firestarter_*.hex` artifacts per board (Uno +
   Leonardo). GATE-02 preserved: stable `main`-push behavior + existing
   `build.yml` artifacts byte-identical to pre-v1.4.

4. **Beta-aware firmware downloader (Phase 18 — INST-01/02/03/04).** Scope
   amendment 2026-05-20 added a narrow CLI carve-out to make the published beta
   firmware actually installable. `firestarter --install` (no flags) preserves
   byte-identical stable behavior; `--pre` fetches highest PEP 440 pre-release;
   `--firmware-version X.Y.ZbN` pins exact tag via `/releases/tags/{tag}`;
   `firestarter firmware list [--all|--pre|--stable]` enumerates releases.
   `_compare_versions` refactored to PEP 440-safe via `packaging.version.Version`.

5. **Documentation (Phase 19 — DOC-01/02/03).** App + firmware READMEs grew
   Beta channel sections (install via `pip install --pre` + `firestarter --install
   --pre/--firmware-version`/`firmware list`; stability guarantee; issue-reporting
   guidance). Meta-repo `.planning/v1.4-RELEASE-PROCEDURES.md` documents the
   release-engineer cutting workflow end-to-end, consuming `15-LOCKSTEP-PROCEDURE.md`
   verbatim with corrected workflow filenames.

6. **End-to-end acceptance gate (Phase 20 — E2E-01, MS-01).** Real beta cut in
   both repos following the documented procedure; PyPI shows `<BETA_VERSION>`,
   `pip install --pre` works cleanly, firmware GitHub Pre-release page carries
   the expected per-board `.hex` artifacts, both repos' tags string-equal per
   VER-03, beta-installed app's `firestarter fw -i --pre` fetches the matching
   firmware, and stable-installed app's `firestarter fw -i` (no flags) still
   pulls stable firmware (INST-01 non-regression). Verified via the automated
   `.planning/v1.4-e2e-verify.sh` (PyPI + GitHub Releases API checks) and the
   6-test operator checklist `20-HUMAN-UAT.md`.

### Stats

| Metric | Value |
|--------|-------|
| Phases | 6 (numbered 15-20) |
| Plans | 10 (Phase 15 = 4, Phase 16 = 1, Phase 17 = 1, Phase 18 = 2, Phase 19 = 1, Phase 20 = 1) |
| Requirements | 16/16 mapped, 16/16 shipped (E2E-01 + MS-01 close on operator green) |
| Meta-repo commits | 56 (`git log --oneline 261a430^..HEAD | wc -l` — from `docs(15): capture phase context` to ship) |
| Firmware sub-repo commits | 13 (`git log --oneline 6c66b29^..origin/beta | wc -l` — from `test(15-01): wave 0 scaffold` to 3.0.0b3 cut) |
| Host sub-repo commits | 17 (`git log --oneline a7390cc^..origin/beta | wc -l` — from `test(15-01): wave 0 scaffold (app)` to 3.0.0b3 cut) |
| Live cut iterations | 3 (`3.0.0b1` → `3.0.0b2` → `3.0.0b3`; b1 cut surfaced 5 substrate fixes E2E-01..05, b2 added firmware.py parser fix E2E-06, b3 added .pyc hygiene) |
| Hardware flash validated | Uno (`/dev/ttyACM0`) + Leonardo (`/dev/ttyACM1`) at `3.0.0b3` via `firestarter fw -i --pre` end-to-end |
| New workflow files | 2 (`firestarter_app/.github/workflows/beta-release.yml`, `firestarter/.github/workflows/beta-build.yml`) |
| Existing workflow files modified | 0 (additive only — GATE-01/GATE-02 preserve stable verbatim) |
| New CLI flags on `firestarter` | 3 (`--pre`, `--firmware-version`, `firmware list`) |
| New planning docs | `.planning/v1.4-RELEASE-PROCEDURES.md`, `.planning/v1.4-e2e-verify.sh`, `.planning/v1.4-archive.sh`, `15-LOCKSTEP-PROCEDURE.md`, `lockstep-dryrun-fixture.sh` |
| Hardware impact | None (software-only milestone; no firmware behavior change, no chip support change) |

### Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Branch-driven beta (push to `beta` branch) | Mirrors current `main` -> stable trigger shape; one mental model | Good (single trigger pattern across both pipelines; operator picks the branch, not a tag) |
| PEP 440 pre-release identifiers (`X.Y.ZbN`/`X.Y.ZrcN`) on same PyPI index | TestPyPI adds operator friction; `pip install --pre` is the cleaner opt-in | Good (single source of truth; stable users unaffected) |
| Lockstep mechanism = manually-paired beta-branch push with explicit `BETA_VERSION` input | Rejected alternatives: shared meta-repo VERSION file (cross-repo write coupling), cross-repo `repository_dispatch` (requires cross-repo PAT with `repo` scope) | Good (no new cross-repo trust surface; operator-readable; `lockstep-dryrun-fixture.sh` proves byte-identity) |
| Firmware GitHub Pre-release with `make_latest: false` | `/releases/latest` API automatically filters pre-releases out -- protects stable-installed `firestarter --install` without code changes | Good (INST-01 non-regression preserved via API filtering, not via brittle client-side logic) |
| Stable pipeline preservation (GATE-01 + GATE-02) | v1.4 is additive plumbing; main -> stable behavior byte-identical to pre-v1.4 | Good (zero regressions; verified by independent main-push smoke during Phase 16/17 development) |
| Scope amendment 2026-05-20: add Phase 18 Beta-Aware Firmware Downloader | Without `--pre`/`--firmware-version`/`firmware list`, published beta firmware was uninstallable via `firestarter` CLI -- half a feature | Good (full operator round-trip: cut beta -> install beta app -> install beta firmware via app) |
| Auto-promotion beta -> stable workflow DEFERRED to v1.5+ | Manual fast-forward merge `beta` -> `main` is sufficient for the milestone's first beta cuts; auto-promotion needs real-world usage data before designing | Revisit (when beta channel sees real use) |

### Known Gaps (deferred — pointers to REQUIREMENTS.md Future Requirements)

Per D-15, the following are explicit pointers to existing entries in `.planning/REQUIREMENTS.md`
section "Future Requirements (deferred past v1.4)":

- **Auto-promotion beta -> stable workflow** — `promote.yml` (or equivalent) that fast-forwards
  `beta` -> `main` and bumps to stable in one CI run. Deferred until beta channel sees real use
  and the promotion pattern stabilizes. See REQUIREMENTS.md Future Requirements.

- **Branch-protection rules on `beta` branch** — accidental force-pushes possible today. Add
  post-v1.4 if accidental-push problems surface. See REQUIREMENTS.md Future Requirements.

- **Signed release artifacts** (sigstore / GPG) — both stable and beta ship unsigned today;
  signing is a dedicated milestone covering both at once. See REQUIREMENTS.md Future Requirements.

- **TestPyPI publishing channel** — explicitly rejected for v1.4 (operator friction); could
  revisit if beta operators report needing isolated install testing. See REQUIREMENTS.md
  Future Requirements.

- **Beta installation metrics / telemetry** — not in scope; future release-ops milestone.
  See REQUIREMENTS.md Future Requirements.

- **Per-board `--pre` fallback** — if Uno has a beta but Leonardo doesn't, INST-02's fallback
  policy is unspecified. Add explicit policy in a later milestone if it surfaces. See
  REQUIREMENTS.md Future Requirements.

- **Cached firmware download / offline install** — app always hits GitHub today; cache layer
  is a separate feature. See REQUIREMENTS.md Future Requirements.

### Carry-forward technical debt

Items surfaced during v1.4 development but explicitly NOT cleaned up here (preserves
v1.4's "additive plumbing only" discipline). Each is documented at the listed
phase-local artifact and may be addressed in a follow-on milestone:

- **Phase 17 WR-01** — pre-existing `build.yml` technical debt (vestigial `setup-python@v4` step, `.editorconfig/**` glob).
- **Phase 18 CR-01..CR-03** — pre-existing `update_version.py` code-review findings (atomic file write, none-return crash, rc-series tag fallback).
- **Phase 15 D-25** — `_dev` / `-dev` suffix conventions in version files (e.g. `2.0.7_dev`, `3.0.0-dev`); silently truncated by the version-file parse regex today.

### Hardware impact

None — v1.4 is CI/CD plumbing + consumer-side CLI + docs only. Firmware semantics
stay at v1.2's 3.0.0-dev baseline. No new chip support, no flash budget movement,
no bench session required for milestone close.

---

## v1.2 — Message-ID Logging Rework (Shipped: 2026-05-19)

**Phases:** 4 (numbered 6-9; Phase 10 closed by this milestone-close workflow) | **Plans:** 32 | **Timeline:** 2026-05-08 → 2026-05-19 (~11 days, 108 meta-repo commits, 104 firmware + 64 host sub-repo commits)

**Delivered:** Replaced every firmware text-prefix log emit (`OK:` / `INIT:` / `MAIN:` / `END:` / `INFO:` / `WARN:` / `ERROR:` / `DEBUG:`) with a 1-byte message-ID + raw-byte-param wire protocol driven by a canonical catalog in the meta-repo. The catalog is the single source of truth; codegen emits a C++ header for firmware and a Python module for the host, both regenerated and byte-identity-checked in CI. Old log helpers (`rurp_log`, `rurp_log_P`, `LOG_*_MSG` PROGMEM strings, `log_info_const` / `log_error_format` / `log_warn`) deleted. Leonardo flash 98.7% → **85.4%** (−13.3 pp / −3,792 B of headroom); firmware major bumps to 3.0.0 to enforce lockstep upgrade.

### Flash-Savings Comparison (LMIG-04 acceptance — DOC-02 anchor)

| Snapshot | Leonardo Flash | Uno Flash | SRAM (Uno) | Notes |
|----------|---------------|-----------|------------|-------|
| v1.1 close (baseline) | 28,292 / 28,672 B = **98.7%** | n/a | n/a | Carried v1.1 risk: < 400 B Leonardo headroom |
| v1.2 Phase 6 close | 28,292 B = 98.7% | 26,178 / 32,256 B = 81.1% | 1,593 B | Catalog + helpers landed; no call-sites converted yet (LMIG-01 coexistence proven) |
| v1.2 Phase 7 close | 27,952 B = 97.5% | 25,818 B = 80.0% | 1,593 B | ERROR + WARN + INFO converted (LMIG-02) |
| v1.2 Phase 8 close | 26,096 B = 91.0% | 23,718 B = 73.5% | 1,497 B | State-machine prefix converted (LMIG-03); MSG_DATA_CHUNK streaming (W-04) |
| v1.2 Phase 9 close | 24,500 B = **85.4%** | 22,282 B = 69.1% | 1,497 B | Legacy infra deleted; 3.0.0-dev bump (LFW-03/04, LMIG-04) |
| v1.2 ship | 24,482 B = **85.4%** | 22,262 B = **69.0%** | 1,497 B | Post-ship polish: drop MSG_OK_FW_HANDSHAKE, INFO echo, helper refactor |

### Key Accomplishments

1. **Canonical message catalog + codegen pipeline** (LCAT-01..05, Phase 6 Plan 01)
   — `tools/catalog/messages.toml` is the single source of truth for every log
   message in the system. `tools/catalog/codegen.py` (stdlib-only, deterministic,
   byte-identical re-runs) emits both `firestarter/include/messages.h` (C++) and
   `firestarter_app/firestarter/messages.py` (Python) from the same TOML.
   `sync_to_subrepos.sh` distributes the canonical copy to both sub-repos with
   `diff -q` byte-identity guarantees. CI workflow (`.github/workflows/catalog-
   sync-check.yml` in meta-repo + matching gates in both sub-repos) fails any
   PR that introduces drift.

2. **ID-encoded wire protocol** (LFW-01/02, LHOST-01/02, Phase 6 Plans 02-03)
   — `rurp_log_id(uint8_t id, const uint8_t* params, uint8_t param_count)`
   replaces the legacy `rurp_log(LOG_*_MSG, char*)` family. Wire frame is
   `MAGIC_PREAMBLE | len_u16 | id | params | crc8 | 0x0A` (W-04 wide len
   added in Phase 8 for MSG_DATA_CHUNK > 255 B). Host decoder in
   `serial_comm.py::_decode_id_frame` handles the same shape with WR-03
   guard for text-format catalog entries.

3. **All firmware log call-sites migrated** (LMIG-02, LMIG-03, LFW-03, Phases 7-9)
   — Every text-prefix emit converted across 13 sub-systems
   (`eprom_operations`, `eeprom_28c`, `flash_intel`, `flash_type_3/4`,
   `hardware_operations`, `memory`, `firestarter` main loop, `dev_tools`,
   `json_parser`, plus catalog/helpers). Composite shapes added for
   `MSG_OK_REV` (P-02 [u8, u8]), `MSG_OK_CFG` (P-03 [u32, u32, u8]),
   `MSG_DATA_CHUNK` (W-04 wide bytes), and the host's sentinel-aware
   `_format_message` renderer.

4. **Legacy log infrastructure deletion** (LFW-03/04, Phase 9 Plan 02)
   — Atomic deletion across 23 files: `logging.h` + `logging.c` outright;
   `rurp_log`, `rurp_log_P`, `_firestarter_log_ram`, `_firestarter_log_progmem`,
   `LOG_OK_MSG`, `send_ack`, `send_ack_const`, `debug_setup`, `log_debug`,
   plus all four `#ifdef SERIAL_DEBUG` SoftwareSerial blocks + RX_DEBUG/TX_DEBUG
   defines. `#include "logging.h"` swept from 20 sites. Firmware version
   bumped to `3.0.0-dev` (LFW-05) so the host's `major < 3` guard refuses
   pre-v1.2 firmware cleanly.

5. **Phase 9 flash measurement** (LMIG-04, Phase 9 Plan 05 Task 1)
   — Cold-cache PlatformIO measurement on Leonardo + Uno, two delta tables
   in `09-MEASUREMENT.md`: incremental Phase 8 → Phase 9 attribution and the
   milestone-close v1.1 → v1.2 comparison. SC#1 PROGMEM exemption audit
   landed (12 named-symbol declarations: MAGIC_PREAMBLE + CRC8_TABLE +
   json_parser keys + key_parsers[]; 1 inline `F(...)` literal at LFW-05
   bootstrap; zero uncategorized log-purposed PROGMEM hits).

6. **Post-ship polish: protocol simplification + verbose diagnostics**
   (post-Phase-9 cleanup, ~9 commits) — Dropped per-command `MSG_OK_FW_HANDSHAKE`
   composite (P-04) in favour of a plain `MSG_OK_READY` setup-complete ack;
   added 4 single-purpose INFO emits (`MSG_INFO_FW` / `_HW` / `_PHYSICAL_HW` /
   `_CMD` at 0x5A-0x5D) that mirror the dropped handshake content under the
   `FLAG_VERBOSE` runtime gate. Migrated the EXTRA_INFO_LOGGING build-flag
   block (BUF_VAL, TOKEN_COUNT, FLAG_*, BUFFER_SIZE, MEM_SIZE, ADDR_MASK,
   MATCH_LINES) to SERIAL_DEBUG-gated `DBG_*` sub_ids (0x29-0x35) so the
   diagnostics ride the existing DEBUG channel — zero production wire bytes,
   full breadcrumb chain available in `-D SERIAL_DEBUG` builds.

7. **Host probe path + symbolic command names** — Refactored `_probe_port`
   to send a dedicated `CMD_FW_VERSION` pre-probe with two-ack pattern
   handling (skip setup-complete "Ready", parse "OK: FW: ..." for version
   validation) so the host correctly recognizes 3.0.0-dev firmware without
   the dropped FW_HANDSHAKE in every ack. `COMMAND_NAMES` lookup in
   `constants.py` + a `_format_message` branch renders `MSG_INFO_CMD` as
   "Cmd: 0x0f (HW_VERSION)" and the same annotation applies to `DBG_CMD`
   via the new MSG_DEBUG sub_id decoder path.

8. **Helper-function refactor of macro internals** — Factored
   `LOG_ID_U{8,16,24,32}` byte-pack bodies into `rurp_log_id_u{8,16,24,32}`
   helpers in `rurp_serial_utils.cpp`. The macros collapse to one-liners;
   each call site emits a single CALL instead of inlining the byte-array
   build. Net Flash impact small (−20 B Uno / −18 B Leonardo) since
   AVR-gcc was already inlining well — main value is code cleanliness.

### Stats

| Metric | Value |
|--------|-------|
| Phases | 4 active phases (6-9) + Phase 10 milestone-close (this workflow) |
| Plans | 32 (Phase 6 = 6, Phase 7 = 13, Phase 8 = 8, Phase 9 = 5) |
| Meta-repo commits | 108 |
| Firmware sub-repo commits | 104 |
| Host sub-repo commits | 64 |
| Files changed (meta-repo + planning) | 101 files / +26,173 / −63 |
| Firmware LOC | 4,932 (src + include, C++) |
| Host LOC | 5,200 (firestarter/, Python) |
| Catalog LOC | 1,743 (messages.toml + codegen.py) |
| Native tests | 20/20 PASS (test_dispatch + test_messages) |
| Host pytest | 29/29 PASS (test_decoder + test_fwguard + others) |
| Hardware-bench verified | Uno + Leonardo at 3.0.0-dev, verbose + SERIAL_DEBUG modes |

### Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| ID width = 1 byte | < 100 distinct strings; generous headroom for future growth | ✓ Good (60 catalog entries + 41 DBG sub_ids = 101 total; comfortable) |
| Raw byte params, no type tags on wire | Catalog declares each ID's shape; type tags would waste bytes | ✓ Good (Phase 8 W-04 added `bytes` variable-length shape without protocol break) |
| Codegen output committed to both sub-repos | Operators can build without running codegen first; CI drift gate catches changes | ✓ Good (zero drift incidents; tags ship reproducibly) |
| Phased migration (infra → batched convert → delete last) | Allows both old + new paths to coexist during migration; safer than big-bang | ✓ Good (each phase shipped a working build; LMIG-01 coexistence proven Phase 6) |
| Lockstep upgrade (no backwards compat) | Wire format change too invasive to support both; FW major bump enforces | ✓ Good (3.0.0-dev gate works; host pre-v1.2 refusal clean) |
| MSG_OK_FW_HANDSHAKE → plain MSG_OK_READY (post-ship polish) | Per-command FW echo over-specified; INFO emits handle verbose case better | ✓ Good (saved ~5 wire bytes per command; INFO echo restored visibility) |
| EXTRA_INFO_LOGGING → SERIAL_DEBUG | Build-flag gate is coarser than macro-level; DBG channel already SERIAL_DEBUG-gated | ✓ Good (10 fewer INFO catalog entries; debug breadcrumbs richer) |
| Helper functions for byte-pack | Deduplicate ~10-line macro bodies | ⚠️ Revisit (Flash savings ~20 B — AVR-gcc was already optimizing well; kept for code cleanliness) |

### Known Gaps / Hardware-Pending UAT

Recorded in [STATE.md `## Deferred Items`](.planning/STATE.md). All four items bundle on a single chip-seated W27C512 bench session:

- **Phase 09 Plan 05 Task 3** — chip-seated W27C512 write + readback on both boards (Plan 09-05 hardware UAT)
- **Phase 08 SC#2 / SC#3** — chip-seated UAT carried forward from Phase 8 close (same scope)
- **Phase 08 HUMAN-UAT.md** — 2 pending scenarios (same scope, different artifact)
- **v1.1 debug session `fm1608-fresh-chip-baseline`** — parked since 2026-05-18; unrelated to v1.2 scope (needs different Uno R3 to unblock)

Known deferred items at close: **4** (see STATE.md Deferred Items).

### v1.1 Items Carried Forward (still open after v1.2)

- v1.1 Phase 4 — FM1608 byte-0 read bug (parked, needs different Uno R3)
- WARNING-4 — `firestarter_test.sh` / `write_test.sh` reference deleted `database_generated.json`
- v1.1 DOC-01 — v1.1 milestone close (Phase 5 of v1.1 deferred)

---

## v1.0 — Protocol-Aware Programming Architecture (Shipped: 2026-05-11)

**Phases:** 13 | **Plans:** 22 | **Timeline:** 2026-05-08 → 2026-05-11 (4 days, 66 commits)

**Delivered:** Replaced the guessing-based chip-type pipeline with an explicit
algorithm-first architecture where minipro `protocol_id` flows authoritatively
from upstream XML through the database, wire protocol, and firmware dispatch —
and the firmware executes exactly that algorithm for every chip in the 743-entry
DB. Two safety-critical hazards closed (BLOCKER-1, BLOCKER-2, WARNING-5).

### Key Accomplishments

1. **Algorithm-first wire protocol** (REQ-SER-01, REQ-FW-01) — `firestarter_handle_t`
   carries an explicit `algorithm` integer; `memory.cpp::configure_memory`
   protocol-prefix dispatch covers all 13 KNOWN_PROTOCOLS (0x05/0x06/0x07/0x08/
   0x0B/0x0D/0x0E/0x10/0x27/0x28/0x29/0x35/0x39); legacy `type` enum retained
   as fallback only. Verified by 15/15 Unity dispatch tests on `[env:native]`
   plus `check_dispatch.py` PASS across all 743 chips.

2. **Database pipeline canonicalized** (REQ-DB-01..05, Phases 01 + 11) — Single
   `build_db.py` fetches `infoic.xml` from upstream minipro at runtime,
   parses deterministically to `minipro_complete_db.json` with explicit
   `algorithm` integer, decoded-millivolt `vpp`, correct DIP28 variant splitting
   (`DIP28_27512` / `DIP28_27256` / `DIP28_2764`), unknown-protocol chips
   skipped with WARN. Legacy `parse_db.py`, `infoic.xml`, `verified.txt`,
   `database_generated.json`, `pin-maps.json` all removed.

3. **Five new firmware handlers** — `configure_eprom` (UV-EPROM STD/QUICK/LEGACY,
   Phase 03), `configure_flash3` (AMD-style sector erase, Phase 04),
   `configure_flash_intel` (Intel command-register flash, Phase 05),
   `configure_eeprom28c` (AT28C SDP-disable + DQ7-polling page write, Phase 06),
   `configure_sram` (5V SRAM safe no-op, Phase 12).

4. **Pre-write safety stack** (REQ-SAF-01/02/03, Phases 03 + 07) — VPP ADC
   compare before first write pulse on UV-EPROM and 28C-EEPROM paths;
   chip-ID validation for Intel + AMD + UV-EPROM (`A9_VPP_ENABLE` sequence
   for 27Cxxx); blank check across Flash/EEPROM write inits gated by
   `!FLAG_SKIP_BLANK_CHECK`.

5. **Static-pin and address-bus correctness** (REQ-FW-05/06, Phase 10) —
   `static_high_mask` end-to-end (`pinouts.json` static-high-pins → wire JSON
   static-high → `bus_config_t.static_high_mask` → `mem_util_remap_address_bus`
   unconditional OR); replaces hardcoded `pins == 24` heuristic for tied-high
   CE2/NC pins. Dead `READ_WRITE == WRITE_FLAG` condition replaced with the
   physical-reality `if (handle->pins < 32)` plus VPE_TO_VPP/A16-sharing comment.

6. **CLI hardware-compatibility surface** (REQ-UX-01/02, Phase 09) —
   `firestarter search` flags chips with no valid pinout via `[!]` marker;
   `firestarter info --adapter` prints a DIP-mirrored two-column physical-pin →
   RURP-signal table derived entirely from `pinouts.json`, enabling adapter
   wiring without source-code reference.

7. **Three safety-critical close-out phases** —
   - **Phase 11** consolidated the build pipeline to `build_db.py` and removed
     all legacy artifacts (REQ-DB-05; byte-identical regeneration verified).

   - **Phase 12** closed BLOCKER-1 (277 chips fell through to "Memory type
     0x%02x not supported" before the protocol-prefix dispatch) + BLOCKER-2
     (52 SRAM chips routed to `configure_eprom` with 12V VPP regulator on 5V
     parts). Fixed at three layers: firmware dispatch + Python `_ALGO_MEM_TYPE`
     table + `build_db.py` SRAM tagging.

   - **Phase 13** closed WARNING-5 (23 DIP28_2764 5V EEPROMs mistagged in
     upstream minipro as `algorithm=0x07` would have applied 12V to socket
     pin 1 = A14 address line on write). Data-layer-only fix via inline
     3-predicate override in `build_db.py` flipping these chips to `0x0D`
     (`EEPROM_POLL` → `configure_eeprom28c`, pure 5V path with zero VPP
     regulator engagement). Permanent regression guard `_28C_EEPROM_HAZARD_PINOUT`
     in `check_dispatch.py`.

### Stats

- **Files modified:** firmware (Arduino C++) + Python CLI submodules; meta-repo
  tracks `.planning/` only

- **Verification:** Phase 11 (4/4), Phase 12 (8/8), Phase 13 (8/8) formally
  verified end-to-end. Phases 01-10 verified by independent
  `INTEGRATION-CHECK.md` + Phase 12 `check_dispatch.py` regression on the full
  743-chip DB.

- **E2E flows shipped:** `write -e W27C512`, `write -e AM29F040`,
  `write -e SST39SF040`, `erase -s 0x10000 -e SST39SF040`, `write -e 6116`
  (SRAM safe), `write -e AT28C256` (now safe via Phase 13), `write -e AM28F010`
  (Intel — see Known Gaps), `info <chip> --adapter`, `python tools/build_db.py`.

### Key Decisions

- **Database source:** minipro `infoic.xml` via `build_db.py` (not hand-curated
  JSON). Outcome: ✓ — 743 chips covered without per-chip curation overhead.

- **Wire protocol:** New explicit `algorithm` integer field (minipro
  `protocol_id`); `type` retained as legacy fallback. Outcome: ✓ — all 13
  KNOWN_PROTOCOLS dispatched correctly; no regressions.

- **Firmware dispatch:** Protocol-prefix `if-return` block per KNOWN_PROTOCOLS
  entry in `configure_memory`, mem_type chain retained only for legacy
  user-override DB entries. Outcome: ✓ — verified by Phase 12 `check_dispatch.py`.

- **Packages in scope:** DIP 24, 28, 32 only. Outcome: ✓ — SMD/PLCC/serial
  filtered cleanly by `build_db.py`.

- **WARNING-5 fix:** Data-layer override in `build_db.py` rather than
  per-chip firmware switch. Outcome: ✓ — preserves the "algorithm is
  authoritative" contract while routing around the upstream minipro
  classification error for 23 5V EEPROMs.

### Known Gaps (accepted as tech debt for v1.1)

Captured from `.planning/milestones/v1.0-MILESTONE-AUDIT.md` (status:
`gaps_found`). Audit-time score: 4/18 SATISFIED, 13 PARTIAL (verification-gap
only), 1 UNSATISFIED.

- **REQ-SAF-01 partial — Intel-flash write path** (WARNING-1): `flash_intel_write_init`
  (`firestarter/src/proms/flash_intel.cpp:47-62`) enables `REGULATOR |
  P1_VPP_ENABLE` and delays 500ms before the first write pulse, but never calls
  `rurp_read_voltage_mv()` ADC compare. The UV-EPROM and 28C-EEPROM paths
  satisfy REQ-SAF-01; the Intel-flash family (39 chips, algo=0x10, highest VPP
  in firmware) does not. **Severity: WARNING.** Fix scope: 1-2 lines in
  `flash_intel.cpp`; pattern mirrors `eprom_check_vpp`.

- **Phases 01-10 lack formal VERIFICATION.md files** (verification-gap on 13
  requirements). Wiring is independently verified by `.planning/INTEGRATION-CHECK.md`

  + Phase 12 `check_dispatch.py` (743/743 chips PASS) + Phase 13 hazard guard
  (0 violations) + 15/15 Unity dispatch tests. By the workflow rule "missing
  VERIFICATION.md = unverified phase", 10 of 13 phases remain structurally
  unverified. Optional retroactive `/gsd-validate-phase` runs would close.

- **WARNING-2 — 28C chip-ID forward-compat hazard**:
  `eeprom_28c.cpp::eeprom28c_write_init` ignores `handle->chip_id`. Vacuous
  today (zero 0x0D chips in regenerated DB carry `chip_id_value`) but breaks
  REQ-SAF-02 the moment a user-override or upstream DB change populates
  chip_id for an AT28C-family chip.

- **WARNING-3 — wire-protocol key naming**: JSON `"vpp"` key now carries
  millivolts (was volts) — semantic overload. Recommend renaming wire key to
  `"vpp_mv"`. `firestarter_app/CLAUDE.md` example currently shows a phantom
  `"vpp_mv"` key that is not emitted.

- **WARNING-4 — test-script drift**: `firestarter_test.sh:31` and
  `write_test.sh:17` reference the deleted `database_generated.json`. Breaks
  the documented hardware-integration E2E flow.

- **`build_db.py` robustness**: Bare `except:` at lines ~138-186 (silent chip
  drops + KeyboardInterrupt swallow). `requests.get` lacks `raise_for_status()`
  and `timeout` (non-200 upstream silently overwrites DB). Pre-existing,
  out-of-scope of Phase 11 lock.

- **Lost `verified` field**: `minipro_complete_db.json` no longer carries the
  `verified` field; `database.py::get_eproms(verified=True)` silently returns
  empty. Carried in `11-VERIFICATION.md` follow_ups.

- **DIP24/DIP28/DIP32 `static-high-pins` coverage**: Only DIP24 variants
  populated in `pinouts.json` today. DIP28/DIP32 quirk pins (CE2, JEDEC-tied
  NC) could be added in a future phase (INFO-3).

- **`DIP24_2732` pinout** never appears in regenerated DB (no 24-pin
  variant=0x01 chips survive the DIP/memory-type filter on current
  `infoic.xml`). May be intentional; flag for review.

### Hardware Verification

Not performed in this milestone — no RURP shield available in the dev
environment. All verification was structural (code/DB/dispatch tests). The
documented hardware integration tests (`firestarter_test.sh`, `write_test.sh`)
should be re-run against a physical board before declaring the four
chip-family canon (W27C512, 29F040, SST39SF040, AT28C256) hardware-validated.

---

# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — Protocol-Aware Programming Architecture

**Shipped:** 2026-05-11
**Phases:** 13 | **Plans:** 22 | **Timeline:** 2026-05-08 → 2026-05-11 (4 days, 66 commits)

### What Was Built

- Algorithm-first wire protocol — `algorithm` integer (minipro `protocol_id`)
  flows authoritatively from upstream XML through DB, wire JSON, and into
  `memory.cpp::configure_memory` protocol-prefix dispatch for all 13 known
  protocols
- Five firmware handlers — `configure_eprom` (UV-EPROM), `configure_flash3`
  (AMD), `configure_flash_intel`, `configure_eeprom28c` (5V EEPROM with SDP
  + DQ7 polling), `configure_sram` (safe 5V no-op)
- Canonical database pipeline — single `build_db.py` fetches `infoic.xml`
  from upstream minipro at runtime; 743 chips across DIP24/28/32; legacy
  `parse_db.py` + stale artifacts removed
- Pre-write safety stack — VPP ADC compare (UV-EPROM + 28C paths), chip-ID
  validation, blank check
- Three close-out phases — Phase 11 (pipeline consolidation), Phase 12
  (BLOCKER-1 + BLOCKER-2 three-layer fix), Phase 13 (WARNING-5 data-layer
  override for 23 mis-tagged 5V EEPROMs)

### What Worked

- **Three-layer fixes for safety-critical bugs.** Phase 12 closed BLOCKER-1
  and BLOCKER-2 with parallel fixes in firmware (`configure_memory` dispatch),
  Python (`_ALGO_MEM_TYPE` table in `database.py`), and DB (`build_db.py`
  SRAM tagging). Defense-in-depth — any single layer regressing still leaves
  two correct.
- **Data-layer fix beats firmware switch.** Phase 13's WARNING-5 was tempting
  to fix as a per-chip firmware switch, but an inline 3-predicate override
  in `build_db.py` preserved the "algorithm is authoritative" contract while
  routing around an upstream minipro classification error. 23 chips fixed
  with zero firmware changes (AVR flash delta = 0 bytes).
- **Permanent regression guards.** Phase 12's `check_dispatch.py` SRAM guard
  and Phase 13's `_28C_EEPROM_HAZARD_PINOUT` guard are now load-bearing —
  any future upstream DB drift that re-introduces these hazards will fail
  CI before merge. Cheap to add, high-leverage protection.
- **Algorithm-first commit message convention.** The "BLOCKER closed at
  three layers" / "WARNING closed across three planes" framing in commit
  messages and SUMMARY frontmatter made cross-layer traceability trivial.
- **GSD audit-milestone before close.** The retrospective audit caught
  WARNING-5 as an active hazard introduced by Phase 12 (BLOCKER-1 had
  previously masked it). Without the audit it would have shipped as a
  hardware-damage path. Phase 13 inserted as a dedicated close-out phase.

### What Was Inefficient

- **Phases 01-10 shipped without formal VERIFICATION.md files.** The
  pattern of "VERIFICATION.md per phase" was not enforced until Phase 11.
  Independent verification via INTEGRATION-CHECK + `check_dispatch.py`
  caught the gaps post-hoc, but a retroactive `/gsd-validate-phase` pass
  is now backlog for v1.1.
- **Wire key naming drift.** `"vpp"` was originally volts, then quietly
  became millivolts in Phase 01 without a rename. The semantic overload
  surfaced in the v1.0 audit as WARNING-3 (`firestarter_app/CLAUDE.md`
  example shows a phantom `"vpp_mv"` key that is not emitted). Renaming
  wire keys mid-flight is harder than getting them right up front.
- **REQ-SAF-01 wording vs implementation.** "For every chip" was loose
  enough that the Intel-flash path shipped without VPP ADC compare. The
  UV-EPROM path satisfies it; the Intel-flash path (39 chips) does not.
  Either the requirement should have been tighter ("on every write
  pulse path that asserts VPP > 5V") or the audit-time check stricter.
- **Phase-level scope creep into "documentation" plans.** Phase 12 Plan 05
  and Phase 13 Plan 03 are dedicated documentation plans. They're correct
  in retrospect (CLAUDE.md drifted from the dispatch list), but the
  pattern of "every closing phase needs a doc-sync plan" is worth
  surfacing as an explicit phase template input rather than discovering
  it per phase.

### Patterns Established

- **Three-layer fix for safety-critical bugs.** When a bug crosses firmware /
  Python / DB pipeline, fix it in all three rather than picking one. Cheaper
  than the bug recurring when one layer regresses.
- **Inline override block + permanent regression guard.** Hard-coding an
  override is fine if (a) the predicates are pinned in a comment block
  referencing the audit entry, and (b) a regression guard in
  `check_dispatch.py` makes silent drift impossible.
- **Audit-then-close.** Run `/gsd-audit-milestone` before
  `/gsd-complete-milestone`. The audit caught WARNING-5 as an active
  hazard introduced by closing BLOCKER-1 — a class of regression that
  is invisible at phase-close time.
- **Submodule pointer-bumps in lockstep with planning commits.** Outer-repo
  tracks `.planning/` + sub-repo pointers only. Every code change in
  `firestarter_app/` or `firestarter/` produces a sub-repo commit + an
  outer-repo pointer-bump commit. SUMMARY.md frontmatter pins both SHAs.

### Key Lessons

1. **Algorithm-first beats type-first.** Replacing the lossy `type` byte
   with an explicit `algorithm` integer (minipro `protocol_id`) eliminated
   the entire class of "guess the type from secondary fields" bugs.
   `KNOWN_PROTOCOLS` is now a small, exhaustive, audit-able list.
2. **Closing a blocker can unmask a deeper hazard.** Phase 12 closed
   BLOCKER-1's "Memory type not supported" safe-exit, which had been
   silently protecting 23 AT28C-family 5V EEPROMs from receiving 12V on
   socket pin 1 = A14 during write. Always re-run the audit after a
   blocker is closed; the safe-failure mode you removed may have been
   load-bearing.
3. **Verification gaps are easy to skip on speed runs.** The 4-day
   timeline compressed VERIFICATION.md authoring out of Phases 01-10.
   The codebase is verifiably correct (INTEGRATION-CHECK + 743/743 chip
   dispatch scan) but the artifact gap is real workflow debt. Either
   enforce VERIFICATION.md as a per-phase blocker or accept the gap
   upfront and schedule retroactive validation.
4. **Permanent regression guards are cheap.** Both `check_dispatch.py`
   guards (SRAM, AT28C-hazard) are ~10 lines each and now block silent
   upstream-DB regressions forever. High leverage for trivial cost.

### Cost Observations

- Model mix: not measured this milestone (no telemetry pipeline configured)
- Sessions: not measured
- Notable: 13 phases / 22 plans in 4 calendar days suggests the workflow
  parallelism (multiple plans per phase, audit gates, code-review skill)
  scaled well at this granularity. The bottleneck was thinking time per
  audit decision, not execution time per plan.

---

## Milestone: v1.2 — Message-ID Logging Rework

**Shipped:** 2026-05-19
**Phases:** 4 active (6-9) + Phase 10 milestone-close | **Plans:** 32 | **Timeline:** 2026-05-08 → 2026-05-19 (~11 days, 108 meta-repo commits, 104 firmware + 64 host sub-repo commits)

### What Was Built

A canonical 1-byte-message-ID log protocol replacing every firmware text-prefix emit (`OK:` / `INIT:` / `MAIN:` / `END:` / `INFO:` / `WARN:` / `ERROR:` / `DEBUG:`). A 1,005-line catalog in `tools/catalog/messages.toml` is the single source of truth; deterministic codegen emits a C++ header for firmware and a Python module for the host, both byte-identity-checked in CI. Old log helpers (`rurp_log`, `rurp_log_P`, `LOG_*_MSG` PROGMEM strings, `log_info_const` / `log_error_format` / `log_warn`) atomically deleted across 23 files. Firmware version bumped to 3.0.0-dev to enforce lockstep upgrade. Leonardo Flash 98.7% → **85.4%** (3,792 B headroom restored); native tests 20/20 PASS, host pytest 29/29 PASS, hardware bench verified on Uno + Leonardo with both verbose-mode INFO emits and SERIAL_DEBUG breadcrumb chains.

### What Worked

- **Phased migration cadence (A→B→C→D→Close).** Each phase shipped a working build — the catalog landed without removing anything (Phase 6), then call-sites converted in three layered phases (Phase 7 ERROR/WARN/INFO, Phase 8 state-machine prefixes, Phase 9 delete + measure). At no point was the firmware in a broken state.
- **Codegen-from-canonical with CI drift gate.** The TOML → C++ + Python pipeline had zero drift incidents across 11 days and 108 commits. Generated files committed in both sub-repos meant operators could build without installing the codegen toolchain; CI re-ran codegen and asserted byte-identity to catch any forgotten regen.
- **Atomic legacy deletion in Phase 9 Plan 02.** 23 files, 4 `#ifdef SERIAL_DEBUG` blocks, 20 `#include "logging.h"` sites all deleted in a single coherent commit chain that kept the firmware compiling between commits. Pre-planning via RESEARCH.md "Risks & Landmines" (Risks #1 + #2 enumerating the atomic block) made this safe.
- **Bench-verification on real hardware before milestone close.** Found a real regression (host probe path) that unit tests + native tests had missed. Live bench against Uno + Leonardo with the new firmware caught the false-positive "Firmware outdated" error before users would have hit it.
- **`/gsd-plan-phase` revision loop.** Plan-checker found 8 WARNINGs in Phase 9 plans (FW_VERSION conditional logic, off-by-one line ranges, cwd-sensitive verify chains). The targeted-revision spawn fixed 6/8 in one pass without re-planning from scratch. Stalled at 1 iteration; would have wasted ~2× context budget without the revision loop.

### What Was Inefficient

- **The post-Phase-9 polish cycle (~9 commits over the FW_HANDSHAKE drop chain).** Iterated several times because each "drop X" or "split Y" change broke a downstream protocol expectation discovered only at bench time. The `MSG_OK_FW_HANDSHAKE` drop → host probe break → restore → 2-ack-pattern fix sequence could have been one design pass if I'd traced the host's per-command FW-version check before the firmware edit. Lesson: **read the host's expect_ack / probe path before changing the firmware ack shape**, even for "simple" wire-protocol simplifications.
- **The helper-function refactor for byte-pack macros.** Promised ~200-400 B Flash savings; delivered ~20 B. AVR-gcc was already inlining the pack bodies efficiently — the CALL/RET overhead ate most of the dedup savings. Net code-cleanliness win but not the Flash win the architecture suggested. Lesson: **measure first with `pio run --target=size` before refactoring for size**; the compiler's optimizer is smarter than naive heuristics suggest.
- **REQUIREMENTS.md traceability table maintenance.** Phase 9 reqs (LFW-03 / LFW-04 / LMIG-04) shipped to phase-summary state but the table still showed them as `Pending` at milestone-close time. Needed a manual sweep to mark them Complete. Lesson: **make the requirement-state update part of the phase-close workflow** (post_planning_gaps catches missing coverage but doesn't flip the traceability state on completion).
- **EXTRA_INFO_LOGGING / SERIAL_DEBUG / FLAG_VERBOSE triple-gate maze.** Three different gating mechanisms ended up in the same file. Took several iterations to settle on: build-time `SERIAL_DEBUG` for DEBUG emits, runtime `FLAG_VERBOSE` for INFO emits. Cleaner now but the migration was 3 commits worth of churn.

### Patterns Established

- **Setup-complete + command-output two-ack pattern.** Every firmware command emits `MSG_OK_READY` (setup-complete) followed by the handler's own response. The host's `_probe_port` discards the first ack and parses the second. Code documented at `serial_comm.py:759-800`.
- **Per-command identity echo as INFO emits.** `MSG_INFO_FW` / `_HW` / `_PHYSICAL_HW` / `_CMD` at 0x5A-0x5D give verbose-mode operators the FW version, HW rev, and command on every command response — without spending wire bytes when verbose is off (FLAG_VERBOSE gates the emit).
- **Symbolic command-name annotation via `COMMAND_NAMES`.** Host renders `Cmd: 0x0f (HW_VERSION)` instead of bare hex in both INFO and DEBUG channels. The same lookup applies to MSG_INFO_CMD (production INFO) and DBG_CMD (SERIAL_DEBUG DEBUG) via the host's `_format_message` sentinel-aware renderer.
- **Two-table PROGMEM exemption audit (Risk #8).** SC#1 separates (a) named-symbol PROGMEM declarations (the audit target — must equal documented exemption list) from (d) inline `F("...")` literal sites (anonymous compiler-generated PROGMEM, exempt by definition). Prevents double-counting and gives the operator a clear gate.

### Key Lessons

- **Wire-protocol changes need a host-side trace before the firmware edit.** Even "simple" simplifications can break per-command parsing assumptions. The host's `_probe_port` and `expect_ack` chain are the contract — read them first.
- **Measure compiler output before refactoring for code-size wins.** AVR-gcc with `-Os` inlines small bodies aggressively. Helper-function patterns that look like wins on paper can wash out or even regress slightly when the call/ret overhead exceeds the dedup savings.
- **Verbose-build and production-build behaviors must both be designed up front.** Three different gates (`-D EXTRA_INFO_LOGGING`, `-D SERIAL_DEBUG`, runtime `FLAG_VERBOSE`) competed for the same role. Pick one severity level per use case, gate it at the macro/runtime layer that matches when you want to flip the switch (build-time = SERIAL_DEBUG for DEBUG; runtime per-command = FLAG_VERBOSE for INFO).
- **The bench is the truth — get to it as early as possible.** Hardware-bench revealed the host probe regression in minutes. The same defect was invisible to unit tests, native dispatch tests, and `pio test -e native`. For wire-protocol work specifically, schedule a bench session into every plan, not just the closing one.
- **Symbolic-name annotations earn their wire bytes.** The 13-entry `COMMAND_NAMES` dict + 5-line host render branch is barely any code, but the verbose-log clarity improvement is huge: "Cmd: 0x0f (HW_VERSION)" beats "Cmd: 0x0f" for everyone debugging on the bench.

### Cost Observations

- Model mix: 100% Claude Opus (per project default for this session — the deep wire-protocol work + bench iteration benefited from the larger context budget)
- Sessions: 1 primary session across ~11 calendar days; bulk of post-Phase-9 polish ran in a single long session on 2026-05-19
- Notable: The chip-seated UAT cycle was deliberately deferred to a bench session that can bundle Phase 8 SC#2/SC#3 + Phase 9 SC#3 + (eventually) v1.1 FM1608 unblock all in one chip-handling pass. Avoiding the "one chip-test per phase" anti-pattern saves real operator time.

---

## Milestone: v1.4 — Beta & Pre-release Deployment Pipeline

**Shipped:** 2026-05-20 (single-day cut: planning + execution + live verification + real-hardware flash)
**Phases:** 6 (15-20) | **Plans:** 10 | **Ship tag:** 3.0.0b3

### What Was Built

1. **Versioning + lockstep foundation (Phase 15).** Both sub-repos' `update_version.py` extended to recognize beta-branch context and emit PEP 440 pre-release identifiers (`X.Y.ZbN`/`X.Y.ZrcN`). Shared validation regex across both scripts (string-equality lockstep). `lockstep-dryrun-fixture.sh` cross-script byte-identity proof.
2. **App beta pipeline (Phase 16).** Single-file `firestarter_app/.github/workflows/beta-release.yml` — push:beta + workflow_dispatch + inline pytest gate + version bump + GitHub Pre-release + PyPI publish. GATE-01 preserves stable verbatim.
3. **Firmware beta pipeline (Phase 17).** Single-file `firestarter/.github/workflows/beta-build.yml` — push:beta + workflow_dispatch + catalog/codegen/Unity/PIO gates + version bump + GitHub Pre-release with per-board `.hex`. GATE-02 preserves stable verbatim.
4. **Beta-aware downloader (Phase 18, scope amendment).** `firestarter fw -i --pre`, `fw -i --firmware-version X.Y.ZbN`, `fw --list [--all|--pre|--stable]`. `_compare_versions` refactored to PEP 440-safe via `packaging.version.Version`. INST-01 (stable non-regression) provable via `/releases/latest` API auto-filtering.
5. **Documentation (Phase 19).** Both READMEs grew Beta sections; meta-repo `v1.4-RELEASE-PROCEDURES.md` documents the release-engineer workflow end-to-end.
6. **End-to-end gate (Phase 20).** Real beta cut in both repos following the documented procedure. All 6 E2E-01 sub-criteria green at 3.0.0b3. Real-hardware flash validated on Uno + Leonardo.

### What Worked

- **Substrate-first planning paid off.** Phase 15 (foundation) shipped before Phase 16/17 (consumers) so the version-emission scheme was already in place when the workflow files were written. No retro version-bump fixes were needed across the consumer phases.
- **Sequential app-then-firmware (not parallel).** PyPI's strict PEP 440 + `--pre` semantics shook out the version-emission flow in Phase 16; firmware Phase 17 was a near-mirror that benefited from app lessons-learned. Tight feedback beat parallel throughput.
- **Scope amendment was caught mid-milestone, not post-ship.** When operator surfaced that the published beta firmware would be uninstallable via the existing app, Phase 18 was inserted *after* Phase 15 shipped and *before* Phase 16/17 close — the cleanest possible insertion point.
- **Single-day cut, multi-iteration shipping.** Three sequential beta cuts (b1 → b2 → b3) treated the live cut as the integration test. Each iteration surfaced and fixed a real substrate defect; b3 ships hardened against all six.
- **Real-hardware flash as final E2E.** Going beyond `pip install --pre` to actually flashing both physical Arduinos (Uno on ttyACM0, Leonardo on ttyACM1) caught the firmware.py `FW:` parser bug that would have shipped silently otherwise.

### What Was Inefficient

- **6 substrate defects in the first beta cut (E2E-01..06).** The first beta cut hit five workflow defects sequentially: (a) `publish.yml` didn't auto-trigger after PAT-created release, (b) `pyproject.toml` had conflicting `setuptools_scm` + `setuptools.dynamic[attr]`, (c) `softprops/action-gh-release` defaulted `target_commitish` to pre-bump SHA, (d) `pio run` linked the test-only native env, (e) firmware `Release` step needed PAT but only had `GITHUB_TOKEN`. Each took an iteration to surface. **Lesson:** workflow E2E tests should run against a throwaway tag before the first "real" cut.
- **`.pyc` files committed by auto-commit step.** Phase 15 added new Python files in `.github/scripts/` and `tests/` but `.gitignore` only had narrow per-dir `__pycache__/` patterns. `stefanzweifel/git-auto-commit-action`'s `git add -A` swept the bytecode into beta. Caught at b3. **Lesson:** when a phase adds new Python paths, gitignore audit should be part of plan checker.
- **PyPI listing endpoint vs version endpoint caching.** The verifier's `gh release view --json isLatest` field was removed in current `gh` CLI; verifier needed a `gh api releases/latest` fallback. PyPI's `/pypi/{pkg}/json` listing lagged the version-specific endpoint by ~30s on each cut. **Lesson:** verifier `--quick` mode should poll until propagated, not single-shot.

### Patterns Established

- **"Substrate cut" pattern.** Cut a throwaway version first (`b1` here was effectively a substrate proof) to surface workflow defects in the live environment, then iterate cleanly. Future milestones with new CI/CD plumbing should plan for at least one substrate iteration before considering the cut "the real one".
- **`target_commitish: ${{ steps.auto_commit.outputs.commit_hash }}` for tag placement.** Whenever a workflow does `version bump → auto-commit → release`, the release MUST `target_commitish` the auto-commit SHA, not `github.sha` (which is pre-bump). Both sub-repo workflows now follow this pattern; documented in workflow comments.
- **`paths-ignore` in beta workflows.** Including `.github/**`, `**.md`, `**.sh`, `docs/**` lets workflow-cleanup commits land on beta without triggering an unwanted re-cut. Used successfully to push the publish.yml cherry-pick and the .gitignore fix without auto-bumping.
- **Hardware-flash validation as part of E2E.** Don't trust "package installs from PyPI" as sufficient — actually flash the device and read back the version. Caught the parser bug that two layers of automated CI didn't.

### Key Lessons

1. **Live cuts are integration tests.** Treat the first beta cut of any new CI/CD plumbing as the test, not the ship. Plan for 2-3 iterations.
2. **Auto-commit + tag placement is subtle.** Default `target_commitish` is the trigger SHA, not the post-mutation HEAD. Every workflow that mutates then tags must explicitly pin the target SHA.
3. **`.gitignore` audit is plan-time work.** When a phase adds Python files in new directories, the gitignore patterns must follow. Otherwise auto-commit actions sweep up bytecode.
4. **Real-hardware E2E catches parser bugs.** The `FW: <version>:<board>` parser had been broken since 2025-02 (stable 2.0.7 has it) but only surfaced now because v1.4 added the `--pre` install path. Hardware E2E is the safety net for old code that was never exercised end-to-end.

### Cost Observations

- Single-day milestone (planning + execution + cut + hardware validation + close all on 2026-05-20)
- Commit counts: meta-repo 56 (includes archive + close commits), firmware 13, app 17
- 3 live beta cuts in sequence (b1 → b2 → b3), each ~5 min round-trip from push to PyPI live
- Real-hardware flash via avrdude: ~7s Uno, ~5s Leonardo per chip
- Notable: substrate hardening cost ~6 iterations to land all of E2E-01..06; future beta cuts should land in 1.

---

## Milestone: v1.5 — Arduino Uno (ATmega328PB) Board Support

**Shipped:** 2026-05-21
**Phases:** 5 | **Plans:** 6 | **Timeline:** 2026-05-20 (planning) → 2026-05-21 (execution + bench + close)

### What Was Built

- New `[env:uno328pb]` PIO env using stock `platform = atmelavr` + `board = ATmega328PB` (MiniCore bundled inside atmelavr@5.2.0); no custom board JSON needed (Path B per CONTEXT D-05)
- Atomic 4-site macro-guard widening — inline disjunction `defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_ATmega328PB)` at every site, no umbrella macro (CONTEXT D-02)
- Reworked `name_firmware.py` — PROGNAME derives from `-D RURP_BOARD_NAME` via `env.ParseFlags()`, giving the board-id triple a single source of truth (CONTEXT D-06)
- `default_envs` widened to include `uno328pb` (Phase 22; zero workflow YAML edits needed — existing `firestarter_*.hex` glob picks up the third asset)
- Host CLI `_install_with_avrdude` `uno328pb` elif branch with `("atmega328pb", "urclock", 115200)` profile (Phase 23, bench-validated programmer_id)
- `main.py` argparse `--board` choices widened to `["uno", "uno328pb", "leonardo"]` (Phase 23 D-10 revised)
- 5 new pytest contracts in `test_firmware_install.py` + `_FakeAvrdude` mock helper (Phase 23 TDD shape)
- End-to-end install on real PB silicon proven via `firestarter fw -i --pre` against operator's 328PB-Uno on `/dev/ttyUSB0` (Phase 24 BENCH-01)

### What Worked

- **TDD RED→GREEN shape for Phase 23.** Wave 1 wrote 5 failing tests (3 release-resolution + 1 avrdude profile + 1 argparse allowlist); Wave 2 made them pass with an atomic 2-file edit. Caught the `programmer_id="arduino"` guess as wrong at the bench step — operator's Urclock bootloader exposed it, the 1-line swap fixed it, and the corresponding test assertion was updated in the same fix commit. Test contract continued to pin the new value.
- **CONTEXT.md revision DURING planning.** Phase 23 D-10 was originally written as "no main.py edits" based on incomplete code reading. The researcher surfaced an argparse `choices=["uno", "leonardo"]` constraint, and we revised D-10 (with explicit `(REVISED 2026-05-21 after research)` marker) before the planner ran. Result: the plan included the 1-line argparse fix from the start, no replanning needed.
- **GATE-1.5 byte-identity validation.** Phase 21 captured pre-rework baselines from `firestarter/beta@5fd751e` with `version.h` UNMODIFIED (Pitfall 3 discipline), and Phase 22's verification used `cmp -s` against those baselines to prove uno + leonardo .hex outputs unperturbed. Catches the entire class of "did the macro widening break the existing builds" regressions with a single command.
- **3-shield A/B/C triage methodology.** Operator's standing pattern for hardware-vs-firmware bug isolation rotated through Rev 2.2 → Rev 2.0 → modified Rev 0 shields. Proved the read-jitter bug was hardware-independent (NOT a v1.5 regression) in under 5 minutes; would have taken hours by code inspection alone.

### What Was Inefficient

- **Phase 24 not formally planned** before bench validation started. The operator just said "test that we can install via the app to the pb" and I went directly to bench work. Worked fine here because the scope was operator-driven, but it bypassed the discuss/plan/execute cycle. Should formalize "operator-driven phases" as a documented exception, not an ad-hoc deviation.
- **`firestarter info <chip>` crashed every smoke test attempt** — pre-existing bug in `ic_layout.py:167` where `vpp-pin` is always a list but treated as int. Noticed but not filed as a todo. Should have surfaced more loudly during the smoke test instead of just noting it.
- **Phase 22 BENCH-02 verification cannot byte-compare** due to the read-streaming jitter — discovered during bench validation rather than during plan/research. A "can we actually verify round-trip on this firmware?" smoke test EARLIER in the v1.5 sequence would have surfaced the jitter before BENCH-02 was committed to. Filed as a v1.6 learning.

### Patterns Established

- **CONTEXT.md `(REVISED <date>)` marker** for in-flight decision revisions. When research surfaces something that contradicts an earlier CONTEXT decision, edit the CONTEXT in place with an explicit revision date stamp. Keeps the decision trail visible without losing the original reasoning.
- **3-shield A/B/C triage** as a documented project-level methodology (memory `user-shield-revisions`). Operator owns the practice; the meta-repo just needs to know to ASK which shield when "swap the shield" comes up.
- **Project memory for bench environment** (`project-bench-findings-v15`). Capture operator-hardware specifics that aren't visible from the codebase: port locations, bootloader types, chip-database quirks. Future phases inherit this context for free.
- **`firestarter fw --list --board X` as smoke test** for CI-cut verification. Lists pre-releases that contain `firestarter_X.hex`. Catches a missing release artifact instantly without flashing.

### Key Lessons

- **Bench validation can compress to one session** if (a) the install path is bench-validated end-to-end before going chip-deep, (b) the chip-id command works as a quick "is the socket alive" check, and (c) the operator authorizes destructive writes in advance.
- **CONTEXT decisions get more surprising the closer to silicon you get.** D-10 (Phase 23 argparse) and D-02 (Phase 23 programmer_id) BOTH got revised after research/bench. The lesson is to mark CONTEXT decisions that are "best guess pending bench" explicitly — they're not equal-fidelity with decisions about purely textual code work.
- **3 separate bug findings from one bench session.** Read-jitter (pre-existing, all controllers), EEPROM misclassification (8 chips, pre-existing, blocks erase), `firestarter info` crash (host-side, all chips). None of these blocked v1.5 ship, but they all wanted v1.6 todos. The bench is where pre-existing bugs surface — budget triage time, not just feature-work time.
- **Operator-driven sessions break the GSD ceremony pattern** and that's OK. Phase 24's bench work didn't go through discuss/plan/execute formally — the operator drove it interactively. The output (24-SUMMARY.md, v1.5-BENCH-RESULTS.md) still landed in the right places.

### Cost Observations

- Single-day milestone close (planning landed 2026-05-20, ship 2026-05-21) — comparable to v1.4's same-day cut.
- 6 plans total across 5 phases; Phase 24 had 0 plans (operator-on-bench, no executor agent needed).
- Sub-repo commits very compact: firestarter sub-repo 3 substantive commits + 1 merge; firestarter_app sub-repo 3 + 1 + 1 urclock fix.
- 3 v1.6 backlog items surfaced — appropriate triage-to-ship ratio for a milestone that touches real hardware.

---

## Milestone: v1.10 — Serial Transport Hardening (COBS)

**Shipped:** 2026-06-07
**Phases:** 7 (49–55; 45–48 reserved for v1.9) | **Plans:** 27 | **Tasks:** 36 | **Timeline:** 2026-06-01 (Phase 49 context) → 2026-06-05 (Phase 53 bench close); archived 2026-06-07

### What Was Built

- Custom **streaming COBS `0x00` + CRC8-CCITT** framing layer on the host↔fw data-block path (Phase 50) with decode-in-place + 1-byte lookahead + drain-to-`0x00` automatic resync — the 2 s `len_u16` timeout cascade is gone (recovery ~1 ms for corrupt frames, single bounded ~1 s inter-byte deadline for truncated frames)
- Host→fw JSON command channel migrated into the same framing as a **breaking lockstep wire change** — CRC8 verified before `parse_json()` on every `CMD_IDLE` ingest, replacing the legacy `{`-peek loop (Phase 51); CR-01 OOB-write + CR-02 hang hardened the decoder
- Shared golden-vector catalog (`codegen_vectors.py`) pinning host-encode↔fw-decode byte-identity for data + command frames incl. delimiter-laden + all-delimiter payloads; codegen drift gates green both repos (Phase 52)
- Even-block full-buffer host→fw transfers (no `buffer−2`, Phase 54) + buffer-size advertisement relocated from the FW version string to a `u16` param on the `MSG_OK_READY` ack with a safe-512 default (Phase 55, reverses Phase 54 D-05)
- Operator-witnessed bench corpus (Phase 53): N=5 read + write read-back byte-identity on clean Uno + Leonardo (Rev 2.0); hardware resync proof both directions/both fault forms; uno328pb transport-exoneration verdict — all aggregated at `.planning/v1.10/bench-verification/SUMMARY.md`

### What Worked

- **Decision-phase-first for a load-bearing mechanism choice.** Phase 49 resolved COBS-vs-SLIP with a static SAFE-01 proof + scored matrix BEFORE any implementation committed to a delimiter byte. The `0x00` bus-aliasing question (would framing the command channel make the host emit a frame boundary mid-mode-transition?) was answered on paper, so Phases 50/51 never churned on it.
- **Dual-repo lockstep pinned by codegen + golden vectors.** The `test_messages` Unity suite + host parser tests share a single canonical vector catalog with a CI drift gate (`<regen> && git diff --exit-code`) — same pattern proven in v1.2. Byte-compatibility was provable in CI before the bench, so the hardware session verified transport, not contract.
- **Insert-ahead sequencing held its rationale end to end.** v1.10 was inserted ahead of the paused v1.9 RCA specifically to exonerate the transport. The bench delivered exactly that: clean boards byte-exact, uno328pb instability *persisting* on the hardened transport → serial is now a settled variable, and the residual failure is unambiguously hardware. The methodological prerequisite paid off.
- **Re-sequencing 53 after 54/55.** Phase 55 (CAP-01) shipped changes to the very identity/ack contract the bench would witness; running bench-verification last meant the corpus proves the *final* transport, not a soon-to-change mechanism. Phase 53-07 was added to widen the corpus to the post-55 contract rather than re-running everything.

### What Was Inefficient

- **STATE.md body drifted from git reality.** The frontmatter said 100% / 7 phases while the body still read "Phase 53 pending verification" and the Roadmap Summary still listed only phases 49–53. A stale CLOSE-OUT-GAPS report (committed 09:53) also pre-dated the afternoon bench session (13:12–14:08) and the passing VERIFICATION.md (16:00) — three artifacts telling different stories about the same phase. Cost reconciliation time at close.
- **REQUIREMENTS.md lagged the inserted phases.** EVEN-01 (Phase 54) stayed `[ ]` after the phase verified, and CAP-01 (Phase 55) was never added to the requirements doc at all — the same checkbox-lag pattern the Phase 53 VERIFICATION.md flagged for XACT-03. Inserted phases need a requirements-doc update as part of their own close, not at milestone close.
- **Auto-generated MILESTONES accomplishments picked up noise.** The SDK's `milestone complete` extracted plan "Deviations" lines (`1. [Rule 3 - Blocking] …`) as if they were accomplishments. Required a manual rewrite of the entry.

### Patterns Established

- **Decision phase as phase 0 of a mechanism milestone.** When a milestone hinges on one irreversible technical choice (framing delimiter, wire format), spend a dedicated phase resolving it with a written proof + scored matrix before implementation. Freezes the contract; downstream phases don't relitigate.
- **Inserted/decimal phases own their own requirements-doc bookkeeping.** Flip the requirement checkbox + add the traceability row at phase close, not at milestone close — otherwise the milestone-close audit inherits N silent doc-lags.
- **Transport-exoneration as a first-class verdict.** A hardware re-test that *still fails* on the hardened path is a PASS for a transport-hardening milestone, provided the persistence is recorded as exoneration (not a fix) with the RCA explicitly deferred. Structured verdict > "it still doesn't work."

### Key Lessons

- **Reconcile STATE/VERIFICATION/git against each other at close, newest-wins.** Where a phase has a stale gap report and a later passing VERIFICATION.md, the VERIFICATION timestamp + git log are authoritative. Don't trust a single artifact's status field at milestone close — cross-check timestamps.
- **A milestone whose whole point is "rule out variable X" must state plainly whether X was ruled out.** v1.10's deliverable is a *negative* result on the read bug (serial is not the cause) plus a *positive* result on the transport (byte-exact). Both belong in the milestone entry; the hand-off to v1.9 is the negative result.
- **Stacked-branch milestones carry their base's unmerged commits.** v1.10 stacked off the v1.9 tip; merging v1.10 first promotes v1.9's Phase 44 commits too. This was accepted up front (recorded in Key Decisions) — but it makes the v1.9 promotion the moment to untangle, and that's now flagged for the resumed milestone.

### Cost Observations

- 5 development days (2026-06-01 → 06-05) + a 2-day gap to archival (06-07); 27 plans across 7 phases — denser per-day than the hardware-gated milestones, because phases 49–52 were pure software with CI gates and no bench dependency.
- Hardware gating concentrated in one phase (53) at the end, after all software contracts were CI-green — kept the operator bench session short and focused.
- 8 items deferred at close, all out-of-scope/carry-forward — clean triage-to-ship ratio for an interleaved milestone.

---

## Milestone: v1.11 — Complete infoic.xml Decode & Database Correctness

**Shipped:** 2026-06-10
**Phases:** 6 (56–61) | **Plans:** 14 | **Timeline:** 2026-06-08 → 2026-06-10 (3 days) | HOST-ONLY (firmware untouched like v1.8); beta-only, `3.0.0b9` cut operator-gated

### What Was Built

- Authoritative, minipro-source-cited **field dictionary** (13 attributes, CONFIRMED/INFERRED/UNKNOWN) + rewritten `protocol-id.md`/`protocol-flags.md`/`package-details.md` (Phase 56)
- Re-derived `build_db.py` decode: 4 confirmed bugs fixed (`interpret_timing` ×100→µs; `VCC_VOLTAGES` 0x02/0x03; vcc/vdd label swap; `PROTOCOL_MAP` canonicalized) + `check_dispatch.py` extended to a full-class VPP-safety guard keyed on `electrical.type` (Phase 57)
- Principled `resolve_pinout_key` replacing the survey-built guess tables, with the 3 load-bearing safety overrides preserved as explicit rules; 9 × 24-pin AT28C04/16 EEPROMs unblocked host-only via `DIP24_2816` + `0x0D` + two-layer SR-1 review (Phase 58)
- `diff_db.py` per-chip correctness gate vs pinned baseline + `configure_sram` NVRAM audit (Phase 59); DB 734 → 743 chips
- Display layer rewired to `electrical.type` ground truth via a single shared `resolve_type_label` helper — `info` (Phase 60) and `list`/`search` (Phase 61) now agree (EEPROM vs UV-EPROM, no spurious SRAM VPP)
- Post-close operator-driven FM1608 follow-up: SRAM/FRAM `vcc`→`vdd` (5V) normalization, zero-pulse-delay row suppression, chip-ID `-` placeholder

### What Worked

- **Research re-scoped the milestone before a line was written.** The original framing ("expand to all types + add firmware handlers, dual-repo") was overturned by source-grounded research: the hardware-feasible memory set was already covered, the only real gap was ~9 24-pin EEPROMs, unblockable host-only. v1.11 shipped as a host-only software milestone with zero firmware risk — the research phase saved an entire firmware workstream.
- **Field dictionary as the decode authority (phase 0 pattern, again).** Phase 56 produced the source-cited dictionary first; Phase 57's code fixes referenced it rather than re-deriving lookups. Same "resolve the contract before implementing" shape that worked for v1.10's decision phase.
- **Single-source-of-truth helper for view parity.** Routing both `info` and `list`/`search` through one `resolve_type_label` (D-04) made divergence structurally impossible — the IN-01 info-vs-list bug can't recur because there's one code path. The parametrized list-vs-info parity test locks it.
- **Two-pass `_etype` + override-preservation discipline.** The re-derivation explicitly preserved WARNING-5 / fm1608 / 24-pin-skip as rules and proved it via `check_dispatch.py` 0-violations on every regenerated DB — the load-bearing safety overrides survived a guess-table deletion intact.
- **GATE keyed on the right axis (CR-01).** Code review caught that the VPP-safety guard's algorithm predicate was dead code; re-keying it on `electrical.type` made it a genuine superset of WARNING-5. Review-as-correctness, not just style.

### What Was Inefficient

- **REQUIREMENTS.md checkbox lag — third milestone running.** DOC-01/02/03 + GATE-01 stayed `[ ]` after Phase 56 verified 8/8; the milestone-close audit had to reconcile them. v1.10's retro flagged this exact pattern ("inserted/decimal phases own their own requirements bookkeeping") and it recurred for *first-phase* requirements this time.
- **`milestone complete` CLI undercounted + picked up noise — also a repeat.** It reported 5 phases/13 plans (missed Phase 61 entirely, because the ROADMAP milestone *header* still read "Phases 56-59") and extracted a plan "Deviation" line (`1. [Rule 2 - Missing Critical]…`) as an accomplishment. Required a full manual rewrite of the MILESTONES entry — the same noise v1.10 hit.
- **Phase 61 lived in the Backlog section.** It was added as a backlog `### Phase 61` entry rather than into the v1.11 milestone block, so the close had to move it out and the CLI's phase-count keyed off the stale header. Late-added close phases need the ROADMAP milestone header + phase list updated when they're inserted, not at close.
- **SUMMARY `requirements_completed` frontmatter inconsistently populated** (56-02/03, 58-*, 59-02, 61-01 empty) — coverage was only confirmable via the VERIFICATION requirement tables, adding a cross-check step to the audit.

### Patterns Established

- **Research can (and should) shrink scope.** A dedicated research pass that overturns the milestone's premise — proving most of the proposed work is unnecessary — is a high-value outcome, not a detour. Budget for it before roadmapping a "big expansion."
- **Display/presentation correctness as a follow-on phase pair.** When a decode/data fix changes ground truth, the operator-facing surfaces (`info`, then `list`/`search`) trail as their own small phases (60→61) routed through one shared helper — keeps the data milestone from ballooning while still closing the visible gap.
- **Operator-driven post-close polish belongs in the same milestone entry.** The FM1608 fixes landed after the formal close decision but within the milestone theme; recording them in the MILESTONES entry + STATE (with the on-branch commit SHAs) keeps the beta-cut traceable.

### Key Lessons

- **The ROADMAP milestone *header* is load-bearing for tooling.** `milestone complete` counts phases from the header's stated range; a header that says "56-59" while the work spans 56-61 makes the CLI silently undercount. Update the header the moment a close phase is added.
- **Checkbox/metadata lag is now a confirmed cross-milestone failure mode** (v1.10 + v1.11). Worth a process fix: flip the requirement checkbox at *phase* close, not milestone close — or add a verify-time hook.
- **Always hand-verify the auto-generated MILESTONES entry.** Two milestones running, the SDK extraction has produced wrong counts and noise-as-accomplishments. Treat its output as a draft, not the entry.

### Cost Observations

- 3 development days, 14 plans across 6 phases — dense, because every phase was pure host-side software with CI gates and **no bench dependency** (research correctly ruled out firmware + hardware work).
- Zero hardware sessions; the milestone closed entirely on software gates (`check_dispatch.py`, `diff_db.py`, 559-test suite, snapshots) + one operator UAT review of `firestarter info` output.
- 7 items deferred at close, all pre-existing/out-of-scope/v1.9-gated; 2 carried todos resolved and closed (w27c512 misclassification, info-list divergence) — net backlog *shrank*.

---

## Milestone: v1.12 — Firmware Protocol Dispatch Hardening + Skeletons

**Shipped:** 2026-06-16
**Phases:** 8 delivering (62, 63, 64, 65, 66, 67.1, 69, 70) | **Plans:** 22 | **Timeline:** 2026-06-10 → 2026-06-16 (7 days) | First firmware-touching milestone since v1.10; dual-repo lockstep merged to `beta` (no tag), beta cut operator-gated

### What Was Built

- Firmware **fail-closed dispatch**: `protocol != 0` guard in `configure_memory()` routes every non-zero unimplemented protocol to `configure_not_implemented()` (NULL op pointers, no VPP enable) emitting `MSG_ERR_PROTOCOL_NOT_IMPLEMENTED = 0xBB`; legacy `mem_type` fallback preserved only behind `protocol == 0`; named infeasibility arms for 0x11/0x2A/0x2B/0x2C (Phases 62/63/64; 49/49 native tests, Uno 72.4% flash)
- Host **typed handling**: `ProtocolNotImplementedError(EpromOperationError)` + centralized id-0xBB raise in the state-machine ERROR path + subclass-first `map_typed_errors` arm; probe/connect boundary wired so the 0xBB frame reaches the CLI instead of masking as `ProgrammerNotFoundError` (Phase 65, incl. gap-closure 65-02)
- **Capability-honest DB**: `support_status` taxonomy (`protocol-not-implemented`/`adapter-required`/`vpp-exceeds-max`) on every chip; true NMOS VPP (M2716/M2732=25V, M2732A=21V) vs `RURP_VPP_CEILING_MV=22000`; `NON_DISPATCHABLE_ALGO=0x00`; host-refusal guard in `chip_resolver.resolve_chip` (Phase 66); 14 SRAM chips correctly classified + status-specific `info`/refusal narrative (Phase 67.1); DB 743 → 744
- **CLI robustness** (Phase 69, inserted): root-fixed a live `info` `TypeError` (list-valued pin fields vs `<= pin_count` in `ic_layout.py`) + smoke-audited every command surface with regression tests
- **Beta-merge integration** (Phase 70, inserted): re-ported the v1.12 DB pipeline onto v1.11's `resolve_pinout_key`, regenerated the DB, merged both sub-repos to `beta` lockstep

### What Worked

- **Baseline-and-gate before touching firmware (Phase 62 first).** Pinning the 743-chip dispatch baseline + updating `check_dispatch.py` *before* any firmware edit meant the regression gate was accurate the entire time the hazard was being closed — the GATE-01/02-first ordering paid off exactly as the research predicted.
- **Catalog wire change as its own reviewable commit (Phase 63).** Adding 0xBB to `messages.toml` with zero call sites kept the lockstep codegen change auditable in isolation before any code depended on it — clean separation of "define the wire" from "use the wire."
- **Defense-in-depth on the 12V-VPP hazard.** Firmware guard (`protocol != 0`) + data-layer `NON_DISPATCHABLE_ALGO=0x00` + host guard (`resolve_chip` refusal) — three independent layers, so the host guard alone is authoritative even though the gate detector is hollow.
- **Audit caught the real gaps; one consolidated phase closed them.** The first milestone audit returned `gaps_found` (DB-02/DB-04 mapped to never-run phases); rather than executing two thin phases, Phase 67.1 consolidated both into one verified closure (9/9).

### What Was Inefficient

- **Forked off the wrong base — discovered at the merge, not the fork.** v1.12 branched off the *pre-v1.11* beta, so its DB pipeline collided with v1.11's Phase 58 `resolve_pinout_key` rewrite. The collision only surfaced when attempting `v1.12 → beta` at close, forcing an entire unplanned integration phase (70). A base-branch check at fork time would have caught it.
- **Hollow safety gate shipped as accepted tech debt.** The `check_dispatch.py` `non_supported_dispatchable` detector is declared, asserted-empty, and never populated — it reads as a regression detector but cannot fire. Real safety rests on the host guard. Documented and operator-accepted, but it's a false-assurance artifact that should be made real or removed.
- **Requirements/SUMMARY metadata lag — fourth milestone running.** Traceability still labeled DB-02→67 / DB-04→68 (actual: 67.1); several plan SUMMARYs carry empty `requirements-completed`. Same checkbox/frontmatter-lag failure mode flagged in v1.10 and v1.11.
- **Nyquist validation coverage trailed** — 6/8 phases have missing or partial VALIDATION.md. Behavioral coverage held via VERIFICATION.md + integration check, but formal validation-test coverage lagged execution.

### Patterns Established

- **Base-branch provenance is load-bearing for milestone merges.** When a milestone forks while another is in flight, record what it forked from and verify the base is current before close — or budget for an integration phase. "Integration, not conflict-merge" (regenerate generated artifacts, never hand-merge) is the right shape when pipelines diverge architecturally.
- **Honest-reporting milestones: the DB string is the single source of truth.** One `unsupported_reason` string, rendered verbatim by both `info` display and chip-op refusal (Approach A), keeps the operator-facing narrative consistent without parallel message tables.
- **A safety gate must actually be able to fail.** A detector that's asserted-empty-but-never-populated is worse than no gate (false assurance). If the authoritative layer is elsewhere (the host guard), say so explicitly and don't dress up a hollow check as the safety mechanism.

### Key Lessons

- **Check the fork base at fork time, not merge time.** The single most expensive surprise this milestone (an unplanned integration phase) was a stale fork base that went unnoticed for the whole milestone.
- **"Accepted tech debt" for a *safety* artifact deserves a tracked follow-up, not just a note.** The hollow GATE-03 detector is safe today only because the host guard exists; if the host guard ever changes, the hollow gate won't catch it.
- **Insert-phase agility worked again.** Two unplanned phases (69 crash-fix, 70 integration) slotted in cleanly mid-milestone without derailing the close — the GSD phase-insertion flow continues to absorb discovered work well.

### Cost Observations

- 7 days, 22 plans across 8 delivering phases — firmware + host, but **no bench dependency** (provable on the native dispatch harness + pytest, as scoped).
- 2 of 8 phases were unplanned inserts (69, 70) — ~25% of phases were discovered work, both absorbed without a re-plan of the milestone.
- 4 of 8 phases ran `/gsd-secure-phase` (66/67.1/69/70, all threats_open:0) — security verification is now routine for hazard-adjacent phases.
- 7 items deferred at close — identical to the v1.11 deferral set (pre-existing/out-of-scope/v1.9-gated); none v1.12 work.

---

## Milestone: v1.13 — Programming Algorithm Validation + Gap Implementation

**Shipped:** 2026-06-18
**Phases:** 5 delivering (71–74, 76) | **Plans:** 19 | **Timeline:** 2026-06-16 → 2026-06-18 (3 days)

### What Was Built

- A software-first **three-tier validation harness** (Tier-1 native recording-bus
  register stub + per-family Unity suites; Tier-2 host pytest wire round-trips;
  Tier-3 `dev validate-family` HIL runner) + a declarative per-family **matrix**,
  carrying a non-vacuous PASS oracle (Leonardo-only-PASS / negative control /
  live-R1 / uno328pb-N/A) — and zero production firmware flash.
- Closed the v1.12 **hollow GATE-03 tech debt** by actually populating
  `check_dispatch.py`'s `non_supported_dispatchable` detector.
- Bench-validated the 6 families on Leonardo/Rev 2.0 (PARTIAL, hybrid-gated):
  W27C512 Tier-3 authoritative PASS, SST39SF040 flash3 PASS, FM1608 SRAM PASS,
  W29C040 flash4 real-FAIL → fixed (SDP-unlock + data-driven page write +
  `CMD_CHECK_CHIP_ID`); Leonardo flash held at 89.5%.
- Spec-only gaps: named AT28C04/16 `adapter-required` arm + DIP24→DIP32 adapter
  pin-map spec; X88C64 0x34 MEDIUM feasibility verdict — NO chip graduated to
  `supported` (deferred to v1.14).

### What Worked

- **Test-first / evidence-defines-missing** kept the firmware footprint minimal:
  only one genuine bench failure (W29C040) drove a real handler change; the
  suspected SRAM no-op was DISPROVEN by VAL-06 (FIX-01 closed not-needed) rather
  than "fixed" speculatively.
- Software-first tier ordering meant the harness/matrix/validation work consumed
  zero flash, deferring all ceiling pressure to the small fix surface.
- Hybrid bench gating let the milestone close cleanly at PARTIAL coverage —
  SKIP-deferred matrix cells for chipless families are honest, not blocking.

### What Was Inefficient

- Phase 74 split into Wave 1 (software) shipped + Wave 2 (W29C040 HW re-bench)
  deferred, and Phase 75 (erase) never executed — both pushed to v1.14. The
  milestone delivered its *validation* mandate but left two implementation tails.
- The write-path "Empty input" 0xA4 regression (resolved mid-milestone, Option C)
  ate a debug cycle that the per-chunk INIT/END DATA-ack behavior could have
  surfaced earlier.

### Patterns Established

- **Recording-bus register stub** as a flash-free way to prove VPP/algorithm
  safety in native tests without touching hardware.
- **Non-vacuous PASS oracle** — negative controls + board-class verdict mapping
  to kill source==source self-compare false-PASS.

### Key Lessons

- "Feasible set complete" claims decay — RSCH-01 re-confirmed v1.12's set but the
  bench still surfaced a real flash4 algorithm bug. Validation milestones earn
  their keep.
- Graduating chips to `supported` is a distinct, hardware-gated effort — keeping
  it OUT of a validation milestone (→ v1.14) kept scope honest.

### Cost Observations

- 3-day milestone, mostly software; 9 items deferred at close (all pre-existing
  or accepted tech debt, none v1.13 work).

---

## Milestone: v1.14 — Feasible-Gap Implementation

**Shipped:** 2026-06-23
**Phases:** 4 (77–80) | **Plans:** 9 executed of 13 (4 deferred hardware-gated) | **Timeline:** 2026-06-18 → 2026-06-23 (5 days)

### What Was Built

- The **first chip graduations since v1.0**: the 7–8 0x07 EE-EPROMs now auto-erase
  before programming (`FLAG_CAN_ERASE` from canonical `electrical.type`, Phase 77,
  bench-proven W27C512 write→auto-erase→program→verify on Leonardo with SHA match),
  and 4 NMOS UV-EPROMs graduated `vpp-exceeds-max` → `supported` best-effort
  (Phase 79, VPP ceiling 22000→25000 + DB regen).
- Two genuine hardware blockers resolved as **clean, zero-code deferrals**: X88C64
  0x34 (Phase 78 — A6 ALE-routing PCB-BLOCKED, control register fully allocated)
  and AT28C04/16 adapter graduation (Phase 80 — adapter not built / no chip on hand).
- The cross-cutting **SAFE-01/02/03 graduation-gate-last discipline** (drop the host
  guard only after native + wire + bench evidence; `check_dispatch.py` full-DB gate
  green; lockstep constant parity) established in Phase 77 and held milestone-wide.

### What Worked

- **Contingent / branched phase plans** — Phase 78's plan carried an explicit
  proceed-vs-defer gate keyed on the A6 verdict; when ALE proved PCB-blocked the
  DEFER branch executed with zero code and a verified 7/7. Designing the deferral
  path INTO the plan made "no blind handler" a structural outcome, not a judgment call.
- **Honest deferral over forced graduation** — 2 of 4 gaps were physically un-closable
  without hardware the operator chose not to build; FUT-01/03/04 tracked them cleanly
  instead of shipping unverifiable code.
- **Integration check corroborated the verification-gapped phase** — Phase 79 closed
  without a VERIFICATION.md, but the 744-chip dispatch gate + 650 green tests +
  constants parity gave the milestone audit enough to confirm the DB state.

### What Was Inefficient

- A **wrong-rail measurement** (Phase 79 NMOS-01 first run used `firestarter vpp`,
  forcing the dropped ~12V path) produced a superseded NOT-CLEARED verdict + a
  PCB-feedback-resistor mis-diagnosis; the rail correction (VPP vs VPE, 22.4V at max
  pot) only landed on a re-run. Knowing which rail a 0x0B chip actually programs on
  (direct-VPE) up front would have saved a cycle.
- **2 of 4 phases (79, 80) closed without a VERIFICATION.md** — defensible (79
  integration-corroborated, 80 zero-change) but it left the audit at `gaps_found`
  rather than a clean `passed`.

### Patterns Established

- **Best-effort graduation under operator override** — a chip can graduate to
  `supported` on a rail below its rated VPP when the firmware warns-and-proceeds on
  under-voltage (over-voltage stays the hard damage boundary) and the user opts in;
  the definitive bench SHA-match is demoted to informational (FUT), not gating.
- **Plan-level deferral branches with FUT tracking** — hardware-gated phases encode
  the clean-deferral outcome (zero change, chips stay honestly refused, a FUT item
  recorded) as a first-class branch, so a blocked gate is a valid completion.

### Key Lessons

- **Measure the right rail.** For 0x0B chips, VPP (`firestarter vpp`) is the dropped
  path; they program on VPE. A confident wrong-rail reading drove a multi-day
  mis-diagnosis (PCB resistor change "needed") that the operator's DMM later corrected.
- **`gaps_found` ≠ failure.** When every gap is an intentional, operator-authorized,
  FUT-tracked hardware deferral, the audit status is a coverage statement, not a defect
  list — closing on it is the right call.
- **Designing the deferral into the plan beats deciding at execution.** Phase 78/80's
  pre-authored defer branches kept "no blind handler / no unverified graduation" a
  structural guarantee.

### Cost Observations

- 5-day milestone, host-only delta (firmware untouched on `beta`); 55 meta commits +
  5 host code commits. 2 of 4 gaps deferred on hardware (FUT-01/03/04); 9 cross-milestone
  open artifacts re-acknowledged at close (none v1.14 work).

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Days | Key Change                                                |
| --------- | ------ | ----- | ---- | --------------------------------------------------------- |
| v1.0      | 13     | 22    | 4    | Initial — established algorithm-first, three-layer-fix, regression-guard patterns |
| v1.2      | 4 + close | 32 | 11 | Catalog-driven codegen with CI drift gate; phased migration (A→B→C→D→Close); bench-verification as a first-class step; helper-function refactor pattern (mixed result on AVR) |
| v1.4      | 6     | 10    | 1    | Live cuts as integration tests (3 sequential cuts b1→b2→b3 surfaced 6 substrate defects); branch-driven beta with `make_latest:false` + `pip --pre` opt-in; real-hardware flash as E2E gate; manually-paired lockstep coordination (rejected: shared VERSION file, cross-repo dispatch) |
| v1.10     | 7     | 27    | 5    | Decision-phase-first for a load-bearing mechanism choice (COBS vs SLIP, static proof before implementation); dual-repo lockstep pinned by shared golden-vector codegen + CI drift gate; insert-ahead sequencing to exonerate a variable; transport-exoneration as a first-class PASS verdict (hardware still fails → RCA deferred, not a milestone failure) |
| v1.11     | 6     | 14    | 3    | Research-shrinks-scope (overturned "expand + firmware handlers" → host-only); field-dictionary-as-decode-authority (phase 0); single-source-of-truth helper for view parity (one `resolve_type_label` → divergence structurally impossible); display correctness as a follow-on phase pair (60→61); recurring checkbox-lag + auto-MILESTONES-noise confirmed as cross-milestone failure modes |
| v1.12     | 8     | 22    | 7    | Baseline-and-gate before touching firmware (GATE-first ordering); catalog wire change as its own zero-call-site commit; defense-in-depth on the 12V-VPP hazard (firmware guard + data-layer 0x00 + host refusal); insert-phase agility (2 of 8 phases unplanned: 69 crash-fix, 70 integration); **stale fork base** surfaced an unplanned integration phase at merge; hollow-safety-gate shipped as accepted tech debt (host guard authoritative) |
| v1.13     | 5 + close | 19 | 3 | Software-first / flash-free validation tiers; evidence-defines-missing (one bench-FAIL drove the only fix; a suspected bug DISPROVEN, not speculatively fixed); hybrid bench gating closes cleanly at PARTIAL coverage; non-vacuous PASS oracle kills source==source false-PASS |
| v1.14     | 4     | 9 of 13 (4 deferred HW-gated) | 5 | First chip graduations since v1.0 (erase + 25V NMOS best-effort); plan-level deferral branches with FUT tracking (Phase 78/80 closed clean with zero code); best-effort graduation under operator override (warns-and-proceeds rail, definitive bench demoted to FUT); `gaps_found`≠failure when every gap is an intentional HW deferral; wrong-rail measurement cost a debug cycle (VPP vs VPE on 0x0B chips) |

### Cumulative Quality

| Milestone | Verified Phases | Audit Status     | Hazard-Class E2E Flows |
| --------- | --------------- | ---------------- | ---------------------- |
| v1.0      | 3/13 formal (11, 12, 13) + 10 via INTEGRATION-CHECK | gaps_found (REQ-SAF-01 Intel-flash) | 0 (Phase 13 closed AT28C256) |
| v1.11     | 6/6 formal (56–61, all passed) | passed (15/15 reqs, 0 gaps) | 5/5 CLI E2E flows (info/list/search) green; both correctness gates 0-violation on 743 chips |
| v1.12     | 8/8 formal (62–70, all passed) | tech_debt (17/17 reqs, 0 gaps; deferred non-blocking debt) | 5/5 E2E flows wired (fw→host dispatch, host refusal, DB gate, wire parity, beta-merge); 4/8 phases secure-gated threats_open:0; firmware 49/49 native, host 529/530, cov 76.27% |
| v1.14     | 2/4 formal (77, 78 passed); 79/80 deferred without VERIFICATION.md (79 integration-corroborated, 80 zero-change) | gaps_found — but all gaps intentional/operator-authorized hardware deferrals (FUT-01/03/04), not failures | integration PASS (744-chip dispatch gate 0 violations, 0 regressions; 650 host tests; constants parity 8/8); first hardware graduation bench-proven (W27C512 erase cycle, Leonardo) |

### Top Lessons (Verified Across Milestones)

1. Algorithm-first beats type-first (validated in v1.0 by 743-chip dispatch scan)
2. Three-layer fixes beat single-layer fixes for cross-cutting bugs (v1.0 BLOCKER-1, BLOCKER-2; reaffirmed v1.12 defense-in-depth on the 12V-VPP hazard)
3. Audit-then-close — re-run the audit after closing a blocker to surface unmasked hazards (v1.0 WARNING-5 escalation; v1.12 first-audit gaps_found → Phase 67.1 closure → re-audit)
4. Check a milestone branch's fork base before close — a stale base (v1.12 forked off pre-v1.11 beta) forces an unplanned integration phase if caught only at merge

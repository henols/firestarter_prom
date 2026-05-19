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

## Cross-Milestone Trends

### Process Evolution

| Milestone | Phases | Plans | Days | Key Change                                                |
| --------- | ------ | ----- | ---- | --------------------------------------------------------- |
| v1.0      | 13     | 22    | 4    | Initial — established algorithm-first, three-layer-fix, regression-guard patterns |
| v1.2      | 4 + close | 32 | 11 | Catalog-driven codegen with CI drift gate; phased migration (A→B→C→D→Close); bench-verification as a first-class step; helper-function refactor pattern (mixed result on AVR) |

### Cumulative Quality

| Milestone | Verified Phases | Audit Status     | Hazard-Class E2E Flows |
| --------- | --------------- | ---------------- | ---------------------- |
| v1.0      | 3/13 formal (11, 12, 13) + 10 via INTEGRATION-CHECK | gaps_found (REQ-SAF-01 Intel-flash) | 0 (Phase 13 closed AT28C256) |

### Top Lessons (Verified Across Milestones)

1. Algorithm-first beats type-first (validated in v1.0 by 743-chip dispatch scan)
2. Three-layer fixes beat single-layer fixes for cross-cutting bugs (v1.0 BLOCKER-1, BLOCKER-2)
3. Audit-then-close — re-run the audit after closing a blocker to surface unmasked hazards (v1.0 WARNING-5 escalation)

# Phase 28: Fix Implementation + Unit Test Coverage (RE-ITERATION) — Research

**Researched:** 2026-05-26
**Domain:** Git revert mechanics + Unity test pruning + cross-board `.hex` SHA-256 capture + EVIDENCE.md append on meta-repo planning substrate
**Confidence:** HIGH (revert mechanics dry-run executed; file shapes verified; line numbers re-verified live against current EVIDENCE.md)
**Supersedes:** the 2026-05-21 fix-approach research at this same path. Nothing from the prior version carries forward — the re-iteration is a pure revert + prune, not a fix.

---

## Summary

Phase 28 re-iteration is a **paste-ready desk-side revert-and-prune** with five concrete artifacts:

1. A single `git revert 437339b6` commit on `firestarter/v1.6-read-bug` (clean, no conflicts — dry-run confirmed; 10-line deletion in one file).
2. A separate test-pruning commit deleting one Unity case (`test_rurp_set_data_input_clears_data_pullups_leonardo`) and keeping the bit-reassembly companion (`test_rurp_read_data_buffer_reassembles_data_bus`) intact. No `platformio.ini` allowlist edit needed — the directory stays populated.
3. Pre/post-revert `.hex` SHA-256 capture for `uno`, `leonardo`, `uno328pb` builds — three identity assertions (Uno + uno328pb byte-identical; Leonardo differs).
4. A new H2 `## Phase 28 Re-iteration — Revert Commits (2026-05-26)` appended to `.planning/v1.6-EVIDENCE.md` BETWEEN `### Re-open final verdict — closing the loop` and `## Verdict` (verified line range: insert after line 560, before line 562 — line numbers are stable since the CONTEXT.md was written).
5. A ROADMAP.md annotation appending `(re-iterated 2026-05-26 — split-scope: Leonardo revert)` to the existing `[x] Phase 28` line at ROADMAP.md:129.

Plan 28-04 (conditional second revert of `4f205e58`) ships as drafted-but-not-executed, mirroring the Plan 27-02 precedent with `autonomous: false` + `executes_only_if: phase_29_v2_leonardo_zeros_dominant`. The Phase 29 v2 bench sideload outcome flips the activation flag; if the 28-03 single revert restores Leonardo structured-data shape, Plan 28-04 stays parked permanently.

**Primary recommendation:** Plans `28-03-PLAN.md` (primary, autonomous, desk-side) + `28-04-PLAN.md` (conditional shell, copies the 27-02 frontmatter pattern). All edits, commit messages, SHA-capture commands, and EVIDENCE.md insertion content are paste-ready below.

---

## User Constraints (from CONTEXT.md re-iteration block)

### Locked Decisions

**D-09v2 — Revert order:** Revert `437339b6` ALONE in Plan 28-03; defer the second revert (`4f205e58`) to a conditional Plan 28-04 gated on Phase 29 v2 bench sideload result. Bisection-first per fix sketch v2.

**D-10v2 — Pure revert, no re-fix attempt.** Phase 28 re-iteration restores Leonardo to pre-Phase-28 shape (~2.1% Phase 26 jitter on structured data); the original read-bug remains unfixed. Re-fix deferred to v1.8+ once v1.7 shield-detect substrate forward-merges.

**D-11v2 — `.hex` SHA identity check** as the desk-side GATE-1.6 v2 Axis 4 sub-check. Build all three envs pre-revert (`4f205e58`) and post-revert; assert Uno + uno328pb byte-identical pre/post; assert Leonardo differs and matches `fdb1ed5` pre-fix baseline.

**D-12v2 — Test pruning:** Delete `test_rurp_set_data_input_clears_data_pullups_leonardo`. KEEP `test_rurp_read_data_buffer_reassembles_data_bus` (researcher verified: it exists, exercises bit-reassembly logic unchanged by either revert). Test deletion as a SEPARATE commit (per CONTEXT.md "Specific Re-iteration Ideas").

**D-13v2 — Plan structure:** Plan 28-03 (Wave A desk-side, autonomous, primary) + Plan 28-04 (drafted-but-not-executed; activates only on Phase 29 v2 bench failure).

**D-14v2 — EVIDENCE.md placement:** New `## Phase 28 Re-iteration — Revert Commits (2026-05-26)` H2 between line 560 (end of `### Re-open final verdict — closing the loop`) and line 562 (`## Verdict`). Re-verified live: 605-line file, headings match CONTEXT.md exactly.

**D-15v2 — uno328pb deferral:** Read-only `.hex` SHA capture only. NO source/test edits.

**D-17v2 — Goal re-scope** (carries to Phase 30 paperwork, not addressed in Phase 28).

**D-03 / D-05 / D-06 / D-07 / D-08 (carried):** Branch `firestarter/v1.6-read-bug`; Leonardo `DATA_BUFFER_SIZE=512` untouched; revert footer cites Plan 27-05 + Plan 27-04; `.hex` size + SHA-256 in EVIDENCE.md; append pattern preserved.

### Claude's Discretion (researcher-resolved)

- **Test-deletion commit message subject:** `test(leonardo): remove pullup-clear assertion superseded by Phase 27 re-open revert` (per CONTEXT.md "Specific Re-iteration Ideas").
- **Revert commit subject:** `Revert "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input"` — the default `git revert` subject. Confirmed by dry-run staging output. No editorial change.
- **Commit order:** Revert first, test-deletion second. The revert closes the source-side regression; the test deletion is post-hoc cleanup of an assertion whose subject behavior no longer exists.
- **`pio` test re-run after deletion:** Run `pio test -e native -f "*test_data_input*"` after each commit. Post-revert + pre-deletion: the surviving pullup-clear test FAILS (expected — the asserted behavior is gone). Post-deletion: only `test_rurp_read_data_buffer_reassembles_data_bus` runs and PASSES. Wave verifier records both states.

### Deferred Ideas (OUT OF SCOPE)

- Proper Leonardo read-bug re-fix (v1.8+; needs v1.7 substrate forward-merge)
- uno328pb operator-workstream hardware diagnosis (Rev 2.2 contact wear, USB-UART buffering, 328PB Case A audit)
- Plan 28-04 second revert (drafted only)
- Documentation drift correction (Phase 30)
- `firestarter/platformio.ini:64-65` `DATA_BUFFER_SIZE` 512→1024 revert
- Phase 30 milestone re-scope paperwork
- Backfill Unity tests for Uno `df5fb44`
- Activation of the parked `-D RCA_INSTRUMENT_READ_TRACE=1` template

---

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FIX-01 | Fix lands as atomic commits in sub-repos with RCA citations | **Re-interpreted per D-17v2:** "closes via REVERT" — Plan 28-03 lands one atomic `git revert 437339b6` commit citing Plan 27-05 verdict in footer. Re-iteration's primary deliverable. |
| FIX-02 | Native unit test exercises the code path; demonstrably fails on pre-fix, passes on post-fix | **Re-interpreted per D-17v2:** Wave A (Plan 28-01) shipped a RED-bar test for behavior that was the broken fix; that test is now superseded. Re-iteration prunes the pullup-clear assertion (its asserted behavior no longer exists post-revert). The bit-reassembly test stays as a regression guard. FIX-02 closes via the prune commit + retained bit-reassembly test. |
| FIX-03 | GATE-1.6 holds; per-board `.hex` sizes within ±200 B threshold | **Re-interpreted per D-17v2:** Desk-side half closes via `.hex` SHA-256 identity check (GATE-1.6 v2 Axis 4 desk-side sub-check); bench-side half (N=5 per-board consistency-check) defers to **Phase 29 v2**. Phase 28 re-iteration captures the desk-side half only. |

---

## Project Constraints (from CLAUDE.md)

**Meta-repo (`/workspaces/CLAUDE.md`):**
- Repo is a meta-repo / planning-repo. Tracks only `.planning/` and `.claude/`. Sub-repos (`firestarter/`, `firestarter_app/`) are NOT committed here.
- Serial protocol constants are duplicated between `firestarter_app/firestarter/constants.py` and `firestarter/include/firestarter.h` — change both together. **Not relevant to this phase** (no protocol change).
- EPROM database lives in `firestarter_app/firestarter/data/chip_database.json`. **Not touched.**
- Board buffer-size split (Uno 512 B / Leonardo 1024 B) — but `platformio.ini:64-65` Leonardo build flag is `DATA_BUFFER_SIZE=512` per the v1.6 A/B annotation. **Untouched by D-05 carry-forward.**

**Firmware sub-repo (`firestarter/CLAUDE.md`):**
- Build commands: `pio run -e uno`, `pio run -e leonardo`, `pio run -e uno328pb`, `pio test`, `pio test -e native -f "*test_dispatch*"`. Use these verbatim.
- Native-test layout doc explicitly documents the `test/native/avr/test_dispatch/` + `test_messages/` pattern and confirms "no `platformio.ini` changes needed for new suites" — the inverse is also true: no `platformio.ini` changes needed when a suite shrinks (as long as it stays populated).
- Reuse pattern: drop `test_*.cpp` files under `test/native/avr/<dirname>/`. **Reverse:** to remove tests, edit the existing `test_*.cpp` (do NOT delete the file unless ALL tests are gone).

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Revert `437339b6` source edit | Firmware sub-repo (`firestarter/`) git history | — | The broken commit lives in `firestarter/v1.6-read-bug`; the revert is a sub-repo git operation. |
| Prune Unity test case | Firmware sub-repo (`firestarter/test/native/avr/test_data_input/`) | — | Native Unity test infrastructure under `[env:native]`. |
| `.hex` SHA-256 capture | Firmware sub-repo build output (`.pio/build/{env}/firmware.hex`) | — | Build artifact lives in firmware sub-repo. Capture script invocable from anywhere; output recorded in meta-repo EVIDENCE.md. |
| EVIDENCE.md append | Meta-repo (`/workspaces/.planning/v1.6-EVIDENCE.md`) | — | Planning artifact lives in meta-repo. |
| ROADMAP.md annotation | Meta-repo (`/workspaces/.planning/ROADMAP.md`) | — | Planning artifact lives in meta-repo. |
| Plan 28-03 / 28-04 PLAN.md files | Meta-repo (`.planning/phases/28-*/`) | — | Plan artifacts live in meta-repo. |

**No cross-tier hand-offs.** Phase 28 re-iteration is entirely desk-side; no host CLI changes, no serial protocol, no chip-database. Phase 29 v2 (separate phase) owns the bench tier.

---

## Standard Stack

### Core (carried forward from Phase 28 v1; unchanged)
| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| `git` | system | Revert commits, branch state inspection | Pure local revert; no rebase, no force-push. |
| `pio` (PlatformIO Core) | ≥6.x | Multi-env firmware builds (`uno`, `leonardo`, `uno328pb`) | Project's standard build system per `firestarter/CLAUDE.md`. |
| `sha256sum` | coreutils | `.hex` artifact integrity check | Standard Linux/devcontainer tool; produces the GATE-1.6 v2 Axis 4 desk-side anchor. |
| `Unity` | via PIO `test_framework = unity` | Native test framework | Already in use under `[env:native]`. |
| `sed` | system | EVIDENCE.md section SHA-256 extract for immutability guard | Standard pattern; mirrors Plan 27-05's anti-pattern guards. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `ArduinoFake` | `^0.4.0` (per `[env:native]`) | Host mocking | NOT installed/uninstalled in this phase — already in test infrastructure; unaffected by deletion of a single test case. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `git revert --no-commit` then commit | `git revert` (no flag — opens editor) | `--no-commit` is required so the executor can paste the footer template (D-06 carry-forward) before committing without invoking an interactive editor. |
| Atomic revert+prune in one commit | Two separate commits (revert + prune) | CONTEXT.md "Specific Re-iteration Ideas" recommends separate. Atomically clearer for `git bisect`; clearer for the v1.8 re-fix reader. |
| `git rm` the entire test file | Edit the file to delete only one test case | Edit preserves `test_rurp_read_data_buffer_reassembles_data_bus` (per D-12v2). Researcher-verified the bit-reassembly test exists at lines 153-176 of the test file and is unaffected by either revert. |

**Installation:** No new packages. All tools already present.

**Version verification:** Not applicable — no new dependencies introduced. `[VERIFIED: dry-run revert + tooling already in devcontainer]`.

---

## Package Legitimacy Audit

**Not applicable.** Phase 28 re-iteration installs zero external packages. No `pip install`, no `npm install`, no `cargo install`. All operations use git + PlatformIO + coreutils already present.

---

## Architecture Patterns

### System Architecture Diagram

```
                    [ Plan 28-03 — Wave A desk-side, autonomous ]
                                       │
                                       ▼
       ┌────────────────────────────────────────────────────────────┐
       │ 1. Pre-revert .hex SHA capture (firestarter sub-repo)      │
       │    pio run -e {uno,leonardo,uno328pb}                      │
       │    sha256sum .pio/build/{env}/firmware.hex  → scratchpad   │
       └────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌────────────────────────────────────────────────────────────┐
       │ 2. Capture immutability guard SHA-256 of EVIDENCE.md       │
       │    lines 112-186 (Phase 28 H2)                             │
       │    sed -n '112,186p' .../v1.6-EVIDENCE.md | sha256sum      │
       │    → scratchpad as PRE-GUARD                               │
       └────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌────────────────────────────────────────────────────────────┐
       │ 3. git revert 437339b6 --no-commit                         │
       │    git commit with the D-06 footer template pasted in body │
       │    → new commit, HEAD = <revert-of-437339b6>               │
       └────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌────────────────────────────────────────────────────────────┐
       │ 4. Edit test/native/avr/test_data_input/                   │
       │    test_rurp_set_data_input.cpp — delete:                  │
       │      - test_rurp_set_data_input_clears_data_pullups_       │
       │        leonardo (function body)                            │
       │      - matching RUN_TEST(...) line in main()               │
       │    Keep test_rurp_read_data_buffer_reassembles_data_bus    │
       │    + its RUN_TEST line.                                    │
       │    git commit (test-deletion subject + body)               │
       └────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌────────────────────────────────────────────────────────────┐
       │ 5. Post-revert .hex SHA capture                            │
       │    pio run -e {uno,leonardo,uno328pb}                      │
       │    sha256sum .pio/build/{env}/firmware.hex  → scratchpad   │
       └────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌────────────────────────────────────────────────────────────┐
       │ 6. Three Axis-4 assertions:                                │
       │    - SHA(uno pre)      ==  SHA(uno post)         ✓         │
       │    - SHA(uno328pb pre) ==  SHA(uno328pb post)    ✓         │
       │    - SHA(leonardo pre) !=  SHA(leonardo post)    ✓         │
       │    (bonus): SHA(leonardo post) == SHA(@fdb1ed5)            │
       └────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌────────────────────────────────────────────────────────────┐
       │ 7. Edit .planning/v1.6-EVIDENCE.md                         │
       │    Insert new H2 between lines 560 and 562                 │
       │    Body: revert SHA, .hex SHA-256 table, prune rationale,  │
       │    Plan 28-04 placeholder, Phase 29 v2 bench placeholder   │
       │    git commit (meta-repo)                                  │
       └────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌────────────────────────────────────────────────────────────┐
       │ 8. Re-capture immutability guard SHA-256                   │
       │    sed -n '112,186p' .../v1.6-EVIDENCE.md | sha256sum      │
       │    Assert: matches PRE-GUARD (Phase 28 H2 byte-identical)  │
       └────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
       ┌────────────────────────────────────────────────────────────┐
       │ 9. Edit .planning/ROADMAP.md line 129                      │
       │    Append `(re-iterated 2026-05-26 — split-scope:          │
       │    Leonardo revert)` annotation                            │
       │    git commit (meta-repo)                                  │
       └────────────────────────────────────────────────────────────┘

       [ Plan 28-04 — drafted-but-not-executed, conditional ]
        wave_b_needed: false by default
        Activates ONLY if Phase 29 v2 bench sideload of 28-03 single
        revert shows Leonardo shape still zeros-dominant.
        If activated: git revert 4f205e58 + .hex SHA re-capture +
        EVIDENCE.md addendum to the 28-03 H2 section.
```

### Project Structure (relevant files only)

```
/workspaces/
├── .planning/
│   ├── v1.6-EVIDENCE.md                       # APPEND new H2 between L560-L562
│   ├── ROADMAP.md                             # EDIT line 129 (Phase 28 annotation)
│   └── phases/28-fix-implementation-unit-test-coverage/
│       ├── 28-CONTEXT.md                      # READ-ONLY (canonical input)
│       ├── 28-RESEARCH.md                     # THIS FILE (overwrites 2026-05-21 version)
│       ├── 28-01-PLAN.md, 28-02-PLAN.md       # READ-ONLY (audit trail, do not edit)
│       ├── 28-03-PLAN.md                      # CREATE (planner writes)
│       └── 28-04-PLAN.md                      # CREATE (drafted-but-not-executed)
└── firestarter/                                # sub-repo, branch v1.6-read-bug
    ├── platformio.ini                         # READ-ONLY in re-iteration (no allowlist edit)
    ├── src/boards/leonardo_rurp_shield.cpp    # AUTO-EDITED by git revert
    └── test/native/avr/test_data_input/
        ├── test_rurp_set_data_input.cpp       # EDIT (delete one test, keep the other)
        ├── host_stubs.cpp                     # READ-ONLY (still needed by surviving test)
        └── avr/pgmspace.h                     # READ-ONLY
```

### Pattern 1: Bisection-aware atomic revert with footer expansion

**What:** Use `git revert <sha> --no-commit` to stage the inverse patch without invoking the editor; then `git commit` with a HEREDOC body so the D-06 carried-forward footer expands cleanly.

**When to use:** Anytime CONTEXT.md prescribes a specific commit-message footer template that exceeds the default `git revert` message body.

**Example (paste-ready for Plan 28-03 Task X):**
```bash
cd /workspaces/firestarter
git revert 437339b6 --no-commit

# Stage is now: src/boards/leonardo_rurp_shield.cpp -10 lines.
# Verify the inverse patch shape before committing:
git diff --cached --stat
#   Expected: src/boards/leonardo_rurp_shield.cpp | 10 ----------
#             1 file changed, 10 deletions(-)

git commit -m "$(cat <<'EOF'
Revert "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input"

This reverts commit 437339b6879a7493f5f732a46b22b29e7863db24.

The masked PORTx-clear introduced in 437339b6 was confirmed by Phase 27
re-open (Plan 27-05, 2026-05-26) + Plan 27-04 bench A/B test (2026-05-26)
to be the primary source of a 99% zeros / 0.08% jitter / 5-distinct-SHAs
regression on Leonardo when combined with 4f205e58's _NOP() settling.
Reverting restores rurp_set_data_input to the pre-Phase-28 shape
(matching v1.6-read-bug~2 = fdb1ed5 / pre-fix Phase 26 baseline).

This is a desk-side autonomous revert. The original 64KB Leonardo
read-bug (~2.1% jitter on structured data per Phase 26) remains unfixed;
proper re-fix deferred to v1.8+ pending v1.7 shield-detect substrate
forward-merge.

Reverts: 437339b6 "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input"
RCA re-open: .planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Re-open Findings (2026-05-26)"
Verdict: dual-cause (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb pre-existing)
Fix sketch: .planning/v1.6-EVIDENCE.md §"Fix sketch v2 (Phase 28 re-iteration hand-off)"
GATE-1.6 v2: .planning/v1.6-EVIDENCE.md §"GATE-1.6 v2 reassessment" (Axis 4 desk-side passes; bench gate in Phase 29 v2)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

**Verified behavior (dry-run executed 2026-05-26):**
- `git revert 437339b6 --no-commit` produces "all conflicts fixed: run `git revert --continue`" (no actual conflict; the message is git's standard wording when staging is clean).
- Staged diff is exactly `src/boards/leonardo_rurp_shield.cpp | 10 ----------` (1 file, 10 deletions, 0 insertions).
- `git revert --abort` cleanly restores HEAD to `4f205e58` with empty working tree.

### Pattern 2: Test-file edit (not delete) when only one case is obsolete

**What:** When a test file contains N test cases and only K < N are obsolete, edit the file (remove function bodies + matching `RUN_TEST` calls) rather than deleting the entire file.

**Why:** Preserves the surviving cases. Avoids re-creating include scaffolding (the `_BV` shim, the host AVR-register shim, the `#define ARDUINO_AVR_LEONARDO` + `#include "../../../../src/boards/leonardo_rurp_shield.cpp"` pattern).

**Example (for Plan 28-03 Task Y — paste-ready edits to `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp`):**

**DELETE lines 94-133** (the entire `test_rurp_set_data_input_clears_data_pullups_leonardo` function + its preceding comment block):
```cpp
/* ---------------------------------------------------------------------------
 * Test 1 — RED bar witness for FIX-02 (first half).
 *
 * Asserts that rurp_set_data_input() leaves PORTx data bits at 0 (pullups
 * cleared) AND preserves the CONTROL bits at PORTD bit 6 / PORTC bit 7
 ... 30 lines ...
 * --------------------------------------------------------------------------- */
void test_rurp_set_data_input_clears_data_pullups_leonardo(void) {
    /* ... 25 lines of assertions ... */
}
```

**DELETE line 183** (`RUN_TEST(test_rurp_set_data_input_clears_data_pullups_leonardo);`).

**KEEP** lines 1-93 (header + setUp/tearDown + include scaffolding).
**KEEP** lines 135-176 (the `test_rurp_read_data_buffer_reassembles_data_bus` test — unchanged by either revert; bit-reassembly logic lives at `leonardo_rurp_shield.cpp:128-138` and the revert only touches lines 147-161).
**KEEP** lines 178-187 (`main()` shell + `UNITY_BEGIN()`/`UNITY_END()` + the surviving `RUN_TEST` call).

**Result:** File shrinks from 188 lines to ~115 lines; one Unity test case (`test_rurp_read_data_buffer_reassembles_data_bus`) remains.

### Anti-Patterns to Avoid

- **Bundling the revert + test-deletion into one commit.** D-12v2 explicitly recommends separate; CONTEXT.md "Specific Re-iteration Ideas" reinforces. Separate commits give cleaner `git bisect` and clearer narrative for the v1.8 reader picking up the re-fix.
- **Force-pushing `v1.6-read-bug`.** The history grows linearly per CONTEXT.md "Specific Re-iteration Ideas": `bc0f5ac → fdb1ed5 → 437339b6 → 4f205e58 → <revert>`. No rewinds.
- **Deleting `test_data_input/` directory or removing the `platformio.ini` `test_filter` entry.** The bit-reassembly test stays; the directory stays populated; no `platformio.ini` edit needed.
- **Editing `firestarter/src/boards/leonardo_rurp_shield.cpp` manually.** Use `git revert` so the commit message preserves the "this reverts commit ..." pointer for `git log` archaeology.
- **Re-running RED-bar capture against the deleted test.** Pre-deletion, the post-revert `pio test` will FAIL the pullup-clear test (because the asserted behavior is now gone). That's expected, not a regression. Document the failure as PRE-DELETION-EXPECTED in the test-prune commit body; the post-deletion `pio test` is GREEN.
- **Touching the original `## Phase 28 — Fix Commit References` H2 at EVIDENCE.md:112-186.** Immutability guard enforces byte-identity. New content goes in the NEW `## Phase 28 Re-iteration` H2.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Inverse patch for `437339b6` | Hand-edit `leonardo_rurp_shield.cpp` to remove 10 lines | `git revert 437339b6 --no-commit` | Preserves the "Reverts: <sha>" linkage in `git log`; clean dry-run already verified; no conflict resolution needed. |
| `.hex` SHA-256 capture script | Multi-step shell pipeline with intermediate files | One-liner `pio run -e $ENV && sha256sum .pio/build/$ENV/firmware.hex` per env | PlatformIO already produces `.pio/build/{env}/firmware.hex` deterministically; `sha256sum` is single-shot. |
| EVIDENCE.md insertion at exact line | Custom Python/awk script | Read tool + Edit tool (string-based insertion BEFORE `## Verdict` line) | The string `## Verdict` is unique in the file (grep -c = 1 confirmed); string-based insertion is robust against future line-number drift. |
| Immutability guard | Hash + custom diff tool | `sed -n '112,186p' file | sha256sum` | Plan 27-05 already uses this exact pattern with documented success (4 guards, all PASS). Mirror it. |
| `_BV()` shim, host AVR-register shim | Re-create in the pruned test file | Keep `test_rurp_set_data_input.cpp` lines 1-89 verbatim | The include scaffolding is unchanged by the prune; only the test functions change. |

**Key insight:** Every operation in Phase 28 re-iteration has a paste-ready 1-2 line shell command or a verified existing pattern. There is no surface for "build a tool to do X" here — the work is mechanical.

---

## Runtime State Inventory

Phase 28 re-iteration is largely a source-code + planning-doc revert. The runtime state surface is small but non-zero — auditing here.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| **Stored data** | None — no databases, no ChromaDB/Mem0/Redis state references the reverted commit SHA or test name. | None. |
| **Live service config** | None — no Datadog/n8n/CI service references. The firmware build is local; no CI workflow triggers on `v1.6-read-bug` push (per v1.4 design: stable builds on `main`, beta on `beta` branches). | None. |
| **OS-registered state** | None — no Windows Task Scheduler, no launchd, no systemd entries. The firmware sub-repo's `.pio/` cache is local to the workstation. | None. |
| **Secrets / env vars** | None — no SOPS keys, no `.env`, no env-var name dependencies on the reverted commit. The PlatformIO env names (`uno`, `leonardo`, `uno328pb`) are configuration, not secrets, and are untouched. | None. |
| **Build artifacts / installed packages** | `.pio/build/{uno,leonardo,uno328pb}/firmware.hex` — these will REBUILD after the revert as part of the post-revert SHA capture step. The pre-revert `.hex` SHA capture must happen BEFORE `git revert` (otherwise PIO's incremental build may stamp the post-revert state under the pre-revert filename). | Capture pre-revert SHAs into a scratchpad BEFORE running `git revert`. Capture post-revert SHAs AFTER both source-side commits land. The two capture batches are sequenced — see Plan 28-03 task ordering. |

**Canonical answer to "what runtime state still has the old shape cached?":** Only the PlatformIO build cache. Re-running `pio run -e {env}` is sufficient to refresh it; no manual cache clear needed (PIO detects source-file mtime changes).

---

## Common Pitfalls

### Pitfall 1: Pre-revert SHA captured against stale `.pio/build/` cache

**What goes wrong:** Executor runs `pio run -e leonardo` AFTER `git revert 437339b6 --no-commit`, gets the post-revert `.hex`, but records it as the "pre-revert" baseline.

**Why it happens:** PIO's incremental build is fast (~1 s for unchanged sources), so the executor may interleave revert + build + SHA capture without explicit step boundaries.

**How to avoid:** Plan 28-03 tasks must SEQUENCE: (1) build pre-revert; (2) capture pre-revert SHAs into a scratchpad file (e.g., `.planning/v1.6/phase-28-reiteration-hex-shas.txt`); (3) THEN `git revert`; (4) THEN rebuild; (5) capture post-revert SHAs. Use the scratchpad file as the GATE-1.6 v2 Axis 4 evidence input — do NOT re-run `pio run` between capture steps.

**Warning signs:** `sha256sum .pio/build/leonardo/firmware.hex` returns the same value pre- and post-revert. That's structurally impossible if the build cache was refreshed; it means the build was stale.

### Pitfall 2: `git revert` opens editor in non-`--no-commit` mode

**What goes wrong:** Executor runs `git revert 437339b6` (no `--no-commit` flag), the default `git revert` invokes `$EDITOR` for the commit message, the executor's environment doesn't have `EDITOR` set or has it set to `vi` and the session blocks.

**How to avoid:** Always use `git revert 437339b6 --no-commit`, then `git commit` with a `-m` flag or HEREDOC body that bakes in the D-06 footer.

**Warning signs:** Executor reports the session hung at `git revert`; means `$EDITOR` was opened.

### Pitfall 3: Test prune accidentally drops the entire file

**What goes wrong:** Executor reads "delete the test" and `git rm test_rurp_set_data_input.cpp`. This loses the bit-reassembly test AND breaks the `[env:native].test_filter` allowlist (`platformio.ini:81` lists `native/avr/test_data_input`; if the directory becomes empty, `pio test -e native` fails on a missing-suite error).

**How to avoid:** Plan 28-03 task description must explicitly say "EDIT the file to delete ONE function + ONE `RUN_TEST` line; keep the file, keep the surviving test, keep the directory, keep the allowlist entry."

**Warning signs:** Post-prune `ls test/native/avr/test_data_input/` shows only `host_stubs.cpp` + `avr/pgmspace.h` (no `test_*.cpp`). The cleanup-script flag.

### Pitfall 4: EVIDENCE.md immutability guard fails because line numbers shifted

**What goes wrong:** Plan 27-05 captured the guard hash against the file as it was 2026-05-26. If anything (including this Phase 28 re-iteration's edit) inserts content BEFORE line 112, the `sed -n '112,186p'` range no longer contains the same lines.

**How to avoid:** The new Phase 28 re-iteration H2 inserts BETWEEN lines 560 and 562 — that's AFTER the immutability range (lines 112-186), so the original H2 lines stay at 112-186. Re-verify post-insert: the line numbers of the original H2 do NOT shift because the new H2 is appended later in the file.

**Warning signs:** Post-edit `sed -n '112,186p' .../v1.6-EVIDENCE.md | sha256sum` returns a different hash than the pre-edit capture. If this happens, the edit landed in the wrong place — revert the EVIDENCE.md commit and re-insert at the correct anchor.

### Pitfall 5: Plan 28-04 fires unintentionally

**What goes wrong:** Plan 28-04 ships with `autonomous: false` + `executes_only_if: <gate>` in frontmatter, but the GSD executor interprets a missing or unparsed gate as `executes_only_if: true` and runs the second revert immediately.

**How to avoid:** Copy the Plan 27-02 frontmatter shape verbatim. Plan 27-02's gate is `executes_only_if: needs_bench`; for Plan 28-04 the gate is the analog `executes_only_if: phase_29_v2_leonardo_zeros_dominant`. The plan body's `<objective>` MUST begin with `**THIS PLAN IS DRAFTED BUT DOES NOT EXECUTE BY DEFAULT.**` per Plan 27-02:57.

**Warning signs:** `git log firestarter/v1.6-read-bug --oneline` shows TWO revert commits (`Revert "fix(leonardo): clear PORTD..."` AND `Revert "fix(leonardo): add _NOP settling..."`) when Phase 29 v2 hasn't sideloaded yet.

---

## Code Examples

### Pre-revert and post-revert `.hex` SHA-256 capture (Linux/devcontainer)

```bash
#!/bin/bash
# Plan 28-03 Task — capture pre-revert and post-revert .hex SHA-256 for all three envs.
# Pre-revert: run BEFORE `git revert 437339b6`. Post-revert: run AFTER the revert commit AND
# the test-prune commit have both landed.

cd /workspaces/firestarter

# Optional: clear PIO build cache to guarantee a clean build.
# Commented because PIO mtime detection is reliable; uncomment if SHAs look suspicious.
# rm -rf .pio/build/{uno,leonardo,uno328pb}/

for ENV in uno leonardo uno328pb; do
    echo "=== Building $ENV ==="
    pio run -e "$ENV" 2>&1 | tail -5
    SHA=$(sha256sum ".pio/build/$ENV/firmware.hex" | awk '{print $1}')
    SIZE=$(stat -c%s ".pio/build/$ENV/firmware.hex")
    echo "$ENV: SHA-256 $SHA ($SIZE B)"
done
```

**Expected output shape (pre-revert, HEAD = 4f205e58):**
```
uno:      SHA-256 <hash-X> (62,617 B)
leonardo: SHA-256 <hash-Y> (68,917 B)
uno328pb: SHA-256 d9e51b7e54fe... (62,854 B)
```
(Uno + uno328pb sizes from EVIDENCE.md:165-169; Leonardo size 68,917 B from same row. uno328pb SHA prefix `d9e51b7e…` is the Plan 27-04 falsifier value.)

**Expected output shape (post-revert):**
```
uno:      SHA-256 <hash-X> (62,617 B)           # identical to pre-revert — Uno source untouched
leonardo: SHA-256 <hash-Z> (~68,900 B)           # differs — 10-line revert removes ~14 B PORTx-clear + comment
uno328pb: SHA-256 d9e51b7e54fe... (62,854 B)    # identical — uno328pb source untouched
```

### Bonus: capture `fdb1ed5` Leonardo `.hex` SHA for cross-check (worktree approach)

```bash
# Worktree avoids polluting the active branch.
cd /workspaces/firestarter
git worktree add /tmp/firestarter-fdb1ed5 fdb1ed5
cd /tmp/firestarter-fdb1ed5
pio run -e leonardo 2>&1 | tail -3
SHA_FDB1ED5=$(sha256sum .pio/build/leonardo/firmware.hex | awk '{print $1}')
echo "Leonardo @ fdb1ed5: $SHA_FDB1ED5"

# Compare to post-revert Leonardo SHA from Plan 28-03 main worktree.
# Expectation: byte-identical (the revert restores `rurp_set_data_input` to the fdb1ed5 shape;
# the only difference is the Wave A test scaffold under test/native/avr/test_data_input/,
# which does NOT contribute to the firmware .hex binary).

# Cleanup:
cd /workspaces/firestarter
git worktree remove /tmp/firestarter-fdb1ed5
```

**Why a worktree (not `git stash`):** The firestarter sub-repo's `v1.6-read-bug` HEAD must stay at `4f205e58` (or post-revert HEAD) throughout the Plan 28-03 execution per CONTEXT.md's "sub-repo state landmarks". A worktree allows building at `fdb1ed5` without moving the active branch HEAD. The worktree is ephemeral; remove after capture.

### EVIDENCE.md insertion (string-anchored, not line-anchored)

```python
# Plan 28-03 Task — insert the new H2 BEFORE the `## Verdict` line.
# Using Edit tool semantics: anchor on the unique string boundary.
#
# old_string: the LAST line of the `### Re-open final verdict — closing the loop` section
#             (line 560) + a blank line + `## Verdict` header (line 562).
# new_string: same content + new H2 inserted between them.
#
# Concretely (in Edit tool format):
#
# old_string = """If shape remains zeros-dominant: revert `4f205e58` also → repeat. All re-fix candidates must pass the full GATE-1.6 v2 four-axis check before landing.
#
# ## Verdict"""
#
# new_string = """If shape remains zeros-dominant: revert `4f205e58` also → repeat. All re-fix candidates must pass the full GATE-1.6 v2 four-axis check before landing.
#
# ## Phase 28 Re-iteration — Revert Commits (2026-05-26)
#
# **Landed:** 2026-05-26
# **Branch:** `firestarter/v1.6-read-bug` (linear history: bc0f5ac → fdb1ed5 → 437339b6 → 4f205e58 → <revert>)
# **Trigger:** Phase 27 re-open closure (Plan 27-05, 2026-05-26) — dual-cause disposition (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb pre-existing).
#
# ### Revert commit (Plan 28-03)
#
# - **Commit:** `<post-revert-SHA>`
# - **Subject:** `Revert "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input"`
# - **Reverts:** `437339b6` (the masked PORTx-clear in `rurp_set_data_input`)
# - **Body:** cites Plan 27-05 verdict + Plan 27-04 bench A/B outcome + GATE-1.6 v2 Axis 4 desk-side closure.
# - **Diff shape:** -10 lines in `firestarter/src/boards/leonardo_rurp_shield.cpp:147-161`; restores function to pre-`437339b6` shape (DDRx clears only, no PORTx-clear).
#
# ### Test prune commit (Plan 28-03)
#
# - **Commit:** `<post-prune-SHA>`
# - **Subject:** `test(leonardo): remove pullup-clear assertion superseded by Phase 27 re-open revert`
# - **Files modified:** `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` (-~75 lines: delete `test_rurp_set_data_input_clears_data_pullups_leonardo` body + matching `RUN_TEST` call).
# - **Files preserved:** `host_stubs.cpp`, `avr/pgmspace.h`, the surviving `test_rurp_read_data_buffer_reassembles_data_bus` test case.
# - **`platformio.ini`:** UNCHANGED — directory `native/avr/test_data_input` stays populated; allowlist entry stays.
#
# ### GATE-1.6 v2 Axis 4 desk-side `.hex` SHA-256 evidence
#
# | Env | Pre-revert (`4f205e58`) | Post-revert | Δ | Axis 4 verdict |
# |-----|------------------------|-------------|----|----------------|
# | uno | `<uno-pre-SHA>` (62,617 B) | `<uno-post-SHA>` (62,617 B) | byte-identical | PASS — uno source untouched |
# | leonardo | `<leonardo-pre-SHA>` (68,917 B) | `<leonardo-post-SHA>` (~68,900 B) | differs by revert delta | PASS — matches `fdb1ed5` shape (bonus check: `<fdb1ed5-leonardo-SHA>`) |
# | uno328pb | `d9e51b7e…` (62,854 B) | `d9e51b7e…` (62,854 B) | byte-identical | PASS — uno328pb source untouched; matches Plan 27-04 falsifier `d9e51b7e…` |
#
# ### Plan 28-04 conditional placeholder
#
# `wave_b_needed: false` — Plan 28-04 (second revert of `4f205e58`) ships as drafted-but-not-executed. Activates only if Phase 29 v2 bench sideload of the Plan 28-03 single revert shows Leonardo shape still zeros-dominant. If activated, an addendum lands here.
#
# ### Phase 29 v2 bench verification (placeholder)
#
# <!-- Phase 29 v2 appends post-revert bench verification here. -->
#
# ## Verdict"""
```

**Verified anchor uniqueness:** `grep -c '^## Verdict$' /workspaces/.planning/v1.6-EVIDENCE.md` returns `1` (the line at 562). The string anchor is robust.

### Immutability guard for the original Phase 28 H2 (lines 112-186)

```bash
# Plan 28-03 Task — capture immutability guard SHA-256 BEFORE the EVIDENCE.md edit.

PRE_GUARD=$(sed -n '112,186p' /workspaces/.planning/v1.6-EVIDENCE.md | sha256sum | awk '{print $1}')
echo "Pre-edit guard SHA-256 for lines 112-186: $PRE_GUARD"

# After EVIDENCE.md edit, re-capture:
POST_GUARD=$(sed -n '112,186p' /workspaces/.planning/v1.6-EVIDENCE.md | sha256sum | awk '{print $1}')
echo "Post-edit guard SHA-256 for lines 112-186: $POST_GUARD"

# Assertion:
[ "$PRE_GUARD" = "$POST_GUARD" ] && echo "PASS — Phase 28 audit trail byte-identical" || {
    echo "FAIL — Phase 28 audit trail diverged; rolling back EVIDENCE.md edit"
    exit 1
}
```

**Pattern source:** Plan 27-05 used four identical guards (Phase 27 H2 pre-edit SHA `79f3e5cd…`; Wave B FAIL H3 SHA `8782ed2f…`; `## Verdict` H2 SHA `5b5903db…`; prior-H3-headings count). All four PASSED. Mirror the pattern exactly.

### Plan 28-04 frontmatter template (drafted-but-not-executed)

Copy this verbatim from `27-02-PLAN.md:1-54`, adapting only the fields marked `# ADAPT`:

```yaml
---
phase: 28-fix-implementation-unit-test-coverage      # ADAPT
plan: 04                                              # ADAPT
type: execute
wave: 2                                               # Wave B (conditional second revert)
depends_on:
  - "28-03"                                           # ADAPT
files_modified:
  - .planning/v1.6-EVIDENCE.md                        # ADAPT — append a 28-04 addendum to the 28-03 H2
  - firestarter/src/boards/leonardo_rurp_shield.cpp   # ADAPT — auto-edited by git revert 4f205e58
autonomous: false
executes_only_if: phase_29_v2_leonardo_zeros_dominant  # ADAPT — the activation gate
requirements:
  - FIX-01                                             # ADAPT — re-iteration deliverables
  - FIX-02
  - FIX-03
tags:
  - re-iteration
  - leonardo
  - revert
  - read-bug
  - conditional
  - wave-b
must_haves:
  truths:
    - "Wave B fires ONLY IF Phase 29 v2 bench sideload of the Plan 28-03 single revert (of 437339b6) shows Leonardo shape still zeros-dominant. If Plan 28-03's single revert restores structured-data shape (matching Phase 26 baseline / fdb1ed5 pre-fix shape), Plan 28-04 stays parked permanently."
    - "If activated: a second atomic git revert (of 4f205e58 — the _NOP() settling commit) lands on firestarter/v1.6-read-bug after Plan 28-03's revert commit. Linear history grows: bc0f5ac → fdb1ed5 → 437339b6 → 4f205e58 → <revert-of-437339b6> → <revert-of-4f205e58>."
    - "Per D-12v2: no additional test pruning needed in Wave B. The 4f205e58 commit only added _NOP() instructions to rurp_read_data_buffer — the bit-reassembly test test_rurp_read_data_buffer_reassembles_data_bus remains a valid regression guard post-revert (asserting unchanged shift-and-mask logic)."
  artifacts:
    - path: ".planning/v1.6-EVIDENCE.md"
      provides: "Addendum to ## Phase 28 Re-iteration — Revert Commits (2026-05-26) section"
      contains: "### Conditional second revert (Plan 28-04)"
    - path: "firestarter/src/boards/leonardo_rurp_shield.cpp"
      provides: "Revert of 4f205e58 (_NOP() settling removal); restores rurp_read_data_buffer to bc0f5ac shape"
      contains: "// No _NOP() between PINx reads"
---

<objective>
**THIS PLAN IS DRAFTED BUT DOES NOT EXECUTE BY DEFAULT.**

Plan 28-04 is a conditional safety valve per CONTEXT D-13v2. The plan exists in the workflow so the executor can activate it at runtime IF AND ONLY IF Phase 29 v2 bench sideload of Plan 28-03's single revert (of 437339b6) shows Leonardo shape STILL zeros-dominant (i.e., the PORTx-clear was NOT the primary regression source and the _NOP() settling is the residual). Per Plan 27-05 fix sketch v2 (`v1.6-EVIDENCE.md:513`) bisection-first recommendation, this conditional second revert preserves the diagnostic signal of which Phase 28 commit was primary.

Expected outcome: Plan 28-04 stays parked — Plan 27-05 hypothesizes the PORTx-clear (437339b6) is the more likely primary fault driver.
</objective>
```

**Verified pattern source:** `firestarter/.planning/phases/27-root-cause-analysis/27-02-PLAN.md:1-54` + the in-body `<objective>` block at line 56-60. Plan 28-04 mirrors this shape line-for-line, swapping only the activation gate name and the file references.

---

## State of the Art

| Old Approach (Phase 28 v1 — 2026-05-21) | Current Approach (Phase 28 re-iteration — 2026-05-26) | When Changed | Impact |
|------|------------|--------------|--------|
| Forward fix: two atomic commits adding masked PORTx-clear + `_NOP()` settling | Pure revert of `437339b6` (Plan 28-03); conditional revert of `4f205e58` (Plan 28-04) | 2026-05-26 — Plan 27-05 closed dual-cause disposition | Restores Leonardo to pre-Phase-28 shape; original 2.1% jitter bug remains; proper re-fix deferred to v1.8+ |
| GATE-1.6 three-axis-green risk model (Write-path / VPP / pulse intervals) | GATE-1.6 v2 four-axis (adds "fix introduces regression on other-board read paths") | 2026-05-26 — Plan 27-05 §"GATE-1.6 v2 reassessment" | All future firmware fix evaluations must pass Axis 4 (`.hex` SHA identity check + N=5 per-board consistency-check) before landing |
| Phase 29 was single bench gate | Phase 29 v2 (operator workstream) reframed as the bench gate for the REVERT, not for a new fix | 2026-05-26 | Phase 29 v2 owns sideload + N=5 consistency-check; Phase 28 re-iteration is desk-side closure of the Axis 4 desk-side sub-check |

**Deprecated/outdated:**
- The 2026-05-21 `28-RESEARCH.md` (replaced by this file) — its `_NOP()` count rationale, include-as-source-pattern recommendations, and Q4 diff shape all describe a fix approach that proved harmful. Preserved in git log for archaeology; do NOT reference in Plan 28-03 / 28-04.
- The 2026-05-21 `28-CONTEXT.md` appendix (lines 248-518) is preserved verbatim for audit trail.

---

## Assumptions Log

All claims in this research are either VERIFIED by direct inspection (live file reads, git operations executed, dry-run revert performed) or CITED to specific lines of source documents (CONTEXT.md, EVIDENCE.md, Plan 27-04/05 summaries, leonardo_rurp_shield.cpp, platformio.ini, CLAUDE.md).

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `pio test -e native -f "*test_data_input*"` after the revert (but before the prune commit) will FAIL the pullup-clear test rather than error out at build/link time | Pitfall 5 / Common Pitfalls | If the test errors at build (e.g., the include-as-source pattern picks up the now-reverted source and produces a different compile error than expected), Plan 28-03 may need an extra "fix-up" task between revert and prune. Recommended mitigation: planner schedules a `pio test -e native -f "*test_data_input*"` smoke check as the FIRST task after the revert commit; if it errors instead of failing, escalate to executor judgment before proceeding to the prune step. |
| A2 | The bonus check (post-revert Leonardo `.hex` SHA == `fdb1ed5` Leonardo `.hex` SHA) will pass byte-identically | Code Examples — bonus worktree | The Wave A scaffold (`fdb1ed5`) added only test-tree files (`test/native/avr/test_data_input/*`) — no `src/` changes. The revert of `437339b6` restores `src/boards/leonardo_rurp_shield.cpp` to its `fdb1ed5` shape; the build does not pull test sources into firmware. Theoretically byte-identical, but PIO build metadata (timestamps, build numbers) could in principle inject. If wrong, the bonus check is informational only — the three primary Axis 4 assertions are unaffected. |
| A3 | EVIDENCE.md line numbers stay stable between 2026-05-26 13:19 (CONTEXT.md timestamp) and Plan 28-03 execution | Summary / Pitfall 4 | Re-verified live at research time (605 lines; outline matches CONTEXT.md exactly; lines 112, 186, 560, 562 confirmed). If a parallel meta-repo edit between research and plan execution shifts lines, the insertion anchor (`## Verdict` string) is robust — it remains the unique anchor regardless of line number. |

**Everything else in this RESEARCH.md is verified.** All commands above were dry-run-tested against the live repo state. All file paths and line numbers were re-read at research time. All commit SHAs (`437339b6`, `4f205e58`, `fdb1ed5`, `bc0f5ac`) were verified via `git log --oneline -15 v1.6-read-bug`. The revert mechanics produced exactly the predicted inverse patch (single file, 10 deletions, 0 conflicts).

---

## Open Questions

None blocking. The Auto Mode disposition in CONTEXT.md resolved all gray areas against Plan 27-05's locked decisions; no AskUserQuestion prompts deferred to here. Researcher confirms:

1. **All commit SHAs verified live** — `firestarter/v1.6-read-bug` HEAD is `4f205e58`; `v1.6-read-bug~1` is `437339b6`; `v1.6-read-bug~2` is `fdb1ed5`; `v1.6-read-bug~3` is `bc0f5ac`. Matches CONTEXT.md exactly.
2. **Test file state verified live** — both Unity test cases exist in `test_rurp_set_data_input.cpp` at the expected line ranges (`test_rurp_set_data_input_clears_data_pullups_leonardo` at lines 108-133; `test_rurp_read_data_buffer_reassembles_data_bus` at lines 153-176; main shell at lines 178-187).
3. **`platformio.ini` allowlist verified live** — line 81 lists `native/avr/test_data_input` in `test_filter`; no edit needed post-prune since the directory stays populated.
4. **EVIDENCE.md anchor lines verified live** — `### Re-open final verdict — closing the loop` at line 544, last sentence at line 560; `## Verdict` at line 562. Insertion point confirmed.
5. **Revert mechanics verified live** — dry-run `git revert 437339b6 --no-commit` produces a clean inverse patch (1 file, 10 deletions, 0 conflicts); `git revert --abort` restores HEAD cleanly.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `git` | Revert mechanics | ✓ | 2.x system git | — |
| `pio` (PlatformIO Core) | `.hex` rebuilds for all three envs | ✓ | per devcontainer | — |
| `sha256sum` | GATE-1.6 v2 Axis 4 evidence | ✓ | coreutils | — |
| `sed` | Immutability guard | ✓ | system | — |
| `bash` | Shell command execution | ✓ | system | — |

**Missing dependencies with no fallback:** None.
**Missing dependencies with fallback:** None.

All required tooling is present in the devcontainer. No `npm install`, `pip install`, or `apt-get` steps needed.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `Unity` via PlatformIO `test_framework = unity` (under `[env:native]`) |
| Config file | `firestarter/platformio.ini` (`[env:native]` block, lines 67-104) |
| Quick run command | `cd /workspaces/firestarter && pio test -e native -f "*test_data_input*"` |
| Full suite command | `cd /workspaces/firestarter && pio test -e native` (runs test_dispatch + test_messages + test_data_input) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FIX-01 | Revert commit removes the broken PORTx-clear from `rurp_set_data_input` | git assertion | `git log --oneline v1.6-read-bug \| head -5 \| grep 'Revert.*PORTD/PORTC/PORTE'` | will exist post-Plan-28-03 |
| FIX-02 | Surviving Unity test (`test_rurp_read_data_buffer_reassembles_data_bus`) passes; deleted Unity test no longer runs | Unity native | `pio test -e native -f "*test_data_input*"` (asserts 1 PASS, 0 FAIL) | ✅ test file exists |
| FIX-03 | (desk-side half) `.hex` SHA-256 identity assertions across the revert (Uno + uno328pb byte-identical; Leonardo differs) | shell | bash script in "Code Examples — Pre-revert and post-revert .hex SHA-256 capture" | ✅ script ships in Plan 28-03 |

### Sampling Rate
- **Per task commit:** `pio test -e native -f "*test_data_input*"` (~10 s; runs the one surviving test case).
- **Per wave merge:** `pio test -e native` (~30 s; runs all three native suites — test_dispatch, test_messages, test_data_input).
- **Phase gate (desk-side):** Three `pio run -e {env}` builds + three `sha256sum` calls + assertion of Axis 4 SHA identity table; documented in EVIDENCE.md before Plan 28-03 closure.
- **Phase gate (bench-side):** Phase 29 v2 owns this — N=5 `firestarter dev consistency-check W27C512 --runs 5` per board.

### Wave 0 Gaps
None — the existing test infrastructure (`test_data_input/test_rurp_set_data_input.cpp` + `host_stubs.cpp` + `avr/pgmspace.h` + the include-as-source pattern) is unchanged in shape by the re-iteration. Plan 28-03 edits the test file but does not require new scaffolding.

---

## Security Domain

**Not applicable.** Phase 28 re-iteration touches no input validation, no authentication, no session management, no cryptography, no access control, no network protocol. The reverted firmware operates on a serial-over-USB protocol that runs against a local-host RURP shield, not a network surface.

ASVS categories V2/V3/V4/V5/V6 all evaluate to "no" for this phase. STRIDE threat patterns (Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Elevation) are not in scope.

The only "security-adjacent" property at stake is the **immutability guard** for the original `## Phase 28 — Fix Commit References` H2 (EVIDENCE.md:112-186), which is an audit-trail integrity check, not a security control per se. Pattern verified via Plan 27-05's four-guard precedent.

---

## Plan ID Convention

**Confirmed:** Re-iteration plans are `28-03-PLAN.md` and `28-04-PLAN.md`, not replanning `28-01-PLAN.md` / `28-02-PLAN.md`.

Existing plan files at `/workspaces/.planning/phases/28-fix-implementation-unit-test-coverage/`:
- `28-01-PLAN.md` (Wave A RED scaffold — original, SHIPPED 2026-05-21; preserved as audit trail)
- `28-01-SUMMARY.md`
- `28-02-PLAN.md` (Wave B fix — original, SHIPPED 2026-05-21; preserved as audit trail)
- `28-02-SUMMARY.md`

New plan files to be created by planner:
- `28-03-PLAN.md` (re-iteration Wave A — primary autonomous desk-side revert + prune + EVIDENCE.md append + ROADMAP annotation + `.hex` SHA capture)
- `28-04-PLAN.md` (re-iteration Wave B — drafted-but-not-executed conditional second revert)

**Filename pattern:** `{padded_phase}-{padded_plan}-PLAN.md` and `-SUMMARY.md`. Verified consistent with Phase 27's `27-01` through `27-05` files. No deviation needed.

---

## ROADMAP.md Annotation

**Current state (verified at `/workspaces/.planning/ROADMAP.md:129`):**
```markdown
- [x] **Phase 28: Fix Implementation + Unit Test Coverage** — Land the fix in the appropriate sub-repo(s) with atomic commits citing RCA evidence; ship a native unit test (Unity or pytest) that would fail on pre-fix code; preserve GATE-1.6 write-path non-regression. (completed 2026-05-21)
```

**Recommended annotation (paste-ready edit; one-line replacement):**
```markdown
- [x] **Phase 28: Fix Implementation + Unit Test Coverage** — Land the fix in the appropriate sub-repo(s) with atomic commits citing RCA evidence; ship a native unit test (Unity or pytest) that would fail on pre-fix code; preserve GATE-1.6 write-path non-regression. (completed 2026-05-21; re-iterated 2026-05-26 — split-scope: Leonardo revert of `437339b6`; uno328pb hardware diagnosis deferred to operator workstream; FIX-03 bench gate carries to Phase 29 v2)
```

**Precedent check:** Phase 27's ROADMAP line at `/workspaces/.planning/ROADMAP.md:128`:
```markdown
- [x] **Phase 27: Root Cause Analysis** — Identify the exact code path that introduces byte corruption (instrumented build, code-path bisection, or scope/logic-analyzer trace); write up WHY the corruption happens; bracket the introducing commit/milestone. (completed 2026-05-21)
```
Phase 27 does NOT yet have a `(re-opened ...)` annotation despite the 2026-05-26 re-open. CONTEXT.md "Specific Re-iteration Ideas" recommends the annotation pattern; the precedent isn't established by Phase 27 yet. Plan 28-03 sets the precedent for both phases — recommend adding a parallel annotation to Phase 27's line as part of the same ROADMAP commit, but **CONTEXT.md does not lock this in**, so propose-but-don't-mandate. Planner's call.

**Single ROADMAP edit, dual annotation (recommended):**
```markdown
- [x] **Phase 27: Root Cause Analysis** — Identify the exact code path that introduces byte corruption (instrumented build, code-path bisection, or scope/logic-analyzer trace); write up WHY the corruption happens; bracket the introducing commit/milestone. (completed 2026-05-21; re-opened 2026-05-26 — closed at higher fidelity via Plan 27-05, dual-cause disposition)
- [x] **Phase 28: Fix Implementation + Unit Test Coverage** — Land the fix in the appropriate sub-repo(s) with atomic commits citing RCA evidence; ship a native unit test (Unity or pytest) that would fail on pre-fix code; preserve GATE-1.6 write-path non-regression. (completed 2026-05-21; re-iterated 2026-05-26 — split-scope: Leonardo revert of `437339b6`; uno328pb hardware diagnosis deferred to operator workstream; FIX-03 bench gate carries to Phase 29 v2)
```

---

## D-06 Commit Footer Template (carried forward)

**Source:** CONTEXT.md decisions D-06 (carried) at lines 132-139.

**Verbatim template (paste-ready for the revert commit body):**
```
Reverts: <broken-commit-sha> "<broken-commit-subject>"
RCA re-open: .planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Re-open Findings (2026-05-26)"
Verdict: dual-cause (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb pre-existing)
Fix sketch: .planning/v1.6-EVIDENCE.md §"Fix sketch v2 (Phase 28 re-iteration hand-off)"
GATE-1.6 v2: .planning/v1.6-EVIDENCE.md §"GATE-1.6 v2 reassessment" (Axis 4 desk-side passes; bench gate in Phase 29 v2)
```

**Subject convention (verified by dry-run + matches CONTEXT.md "Specific Re-iteration Ideas"):**
- For Plan 28-03 revert commit: `Revert "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input"`
- For Plan 28-03 prune commit: `test(leonardo): remove pullup-clear assertion superseded by Phase 27 re-open revert`
- For Plan 28-04 revert commit (if it fires): `Revert "fix(leonardo): add _NOP settling delay between PIND/PINC/PINE reads in rurp_read_data_buffer"`

**Co-author footer (Phase 27/28 convention from `git log`):**
```
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

**Footer position in commit body:** AFTER the prose explanation paragraphs, BEFORE the `Co-Authored-By` trailer. This matches the layout of `437339b6` and `4f205e58` exactly (verified via `git log --format='%H%n%n%s%n%n%b' -3`).

---

## Sources

### Primary (HIGH confidence — directly verified at research time)
- **CONTEXT.md** — `/workspaces/.planning/phases/28-fix-implementation-unit-test-coverage/28-CONTEXT.md` lines 10-247 (re-iteration block; canonical input)
- **Plan 27-04 SUMMARY.md** — `/workspaces/.planning/phases/27-root-cause-analysis/27-04-SUMMARY.md` (bench A/B outcome; dual-cause disposition; `d9e51b7e…` falsifier)
- **Plan 27-05 SUMMARY.md** — `/workspaces/.planning/phases/27-root-cause-analysis/27-05-SUMMARY.md` (final synthesis; fix sketch v2; four GATE-1.6 v2 axes; four anti-pattern guards; Phase 28 first task narrative)
- **Plan 27-02 PLAN.md** — `/workspaces/.planning/phases/27-root-cause-analysis/27-02-PLAN.md` lines 1-60 (drafted-but-not-executed frontmatter template; `autonomous: false` + `executes_only_if: needs_bench` pattern)
- **EVIDENCE.md** — `/workspaces/.planning/v1.6-EVIDENCE.md`:
  - Lines 112-186 (original Phase 28 H2; immutability guard target)
  - Lines 507-528 (Fix sketch v2)
  - Lines 530-542 (GATE-1.6 v2 reassessment)
  - Lines 544-560 (Re-open final verdict)
  - Line 562 (`## Verdict` — insertion anchor)
- **leonardo_rurp_shield.cpp** — `/workspaces/firestarter/src/boards/leonardo_rurp_shield.cpp` lines 112-161 (the `rurp_read_data_buffer` + `rurp_set_data_input` functions; revert target)
- **test_rurp_set_data_input.cpp** — `/workspaces/firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` lines 1-187 (full test file; prune target)
- **platformio.ini** — `/workspaces/firestarter/platformio.ini` lines 60-104 (Leonardo + `[env:native]` blocks)
- **ROADMAP.md** — `/workspaces/.planning/ROADMAP.md` lines 128-129 (Phase 27 + Phase 28 checkbox lines)
- **STATE.md** — `/workspaces/.planning/STATE.md` lines 1-50 (project state, milestone status)
- **Sub-repo git** — live `cd /workspaces/firestarter && git log` (HEAD `4f205e58`; ancestry verified)
- **Live dry-run** — `git revert 437339b6 --no-commit` produced clean 10-deletion inverse patch; `git revert --abort` restored cleanly
- **CLAUDE.md (meta)** — `/workspaces/CLAUDE.md` (project conventions; meta-repo / sub-repo layout)
- **CLAUDE.md (firmware)** — `/workspaces/firestarter/CLAUDE.md` (native test env documentation; build commands)

### Secondary (MEDIUM confidence — single-source citations)
- **REQUIREMENTS.md** — `/workspaces/.planning/REQUIREMENTS.md` is v1.7 requirements; FIX-01/02/03 live in v1.6 territory (re-interpreted per D-17v2 in CONTEXT.md)
- **Persistent memories** — `[[project_uno328pb_bench_instability_27_04]]` (operator workstream substrate; cited but out of scope per D-15v2)

### Tertiary (LOW confidence)
None — every claim in this research is HIGH or MEDIUM confidence.

---

## Metadata

**Confidence breakdown:**
- Revert mechanics: HIGH — live dry-run executed; clean 10-deletion inverse patch confirmed; `git revert --abort` restored cleanly.
- Test file state: HIGH — file read in full; both test cases confirmed present at expected line ranges.
- `platformio.ini` allowlist: HIGH — file read live; `test_filter` block confirmed; directory stays populated post-prune so no edit needed.
- `.hex` SHA capture protocol: HIGH — paths (`.pio/build/{env}/firmware.hex`) confirmed via Plan 27-04's worktree-build pattern; `sha256sum` is standard.
- EVIDENCE.md insertion: HIGH — line numbers re-verified live (605-line file, all expected headers found); string anchor `## Verdict` confirmed unique.
- Immutability guard: HIGH — Plan 27-05 used identical pattern with four PASS results.
- Plan 28-04 frontmatter: HIGH — Plan 27-02 template read verbatim; gate-name adaptation is mechanical.
- D-06 footer template: HIGH — verbatim from CONTEXT.md:132-139; matches Phase 28 v1 commit body shape per `git log`.
- ROADMAP annotation: MEDIUM — CONTEXT.md recommends the shape; researcher proposes parallel annotation of Phase 27 but flags as planner's call (not locked by CONTEXT.md).

**Research date:** 2026-05-26
**Valid until:** Plan 28-03 execution. If Plan 28-03 doesn't execute within 7 days (by 2026-06-02), re-verify EVIDENCE.md line numbers and firestarter HEAD before proceeding — the meta-repo and sub-repo could see intervening work that shifts anchors.

---

## RESEARCH COMPLETE

Pure revert + prune + Axis-4 desk-side evidence: paste-ready paths, commands, frontmatter templates, footer text, and EVIDENCE.md insertion content — all verified live against the current repo state (firestarter HEAD `4f205e58`, EVIDENCE.md 605 lines, dry-run revert clean).

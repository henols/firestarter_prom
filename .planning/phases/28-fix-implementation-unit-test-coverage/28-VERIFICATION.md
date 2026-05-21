---
phase: 28-fix-implementation-unit-test-coverage
verified: 2026-05-21T21:21:49Z
status: passed
score: 5/5 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: none
  previous_score: n/a
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 28: Fix Implementation + Unit Test Coverage Verification Report

**Phase Goal:** "The fix lands in the appropriate sub-repo(s) with the RCA evidence cited in commit messages, and a native unit test (Unity or pytest, whichever sub-repo the RCA points at) exercises the specific code path and would fail on the pre-fix code."

**Verified:** 2026-05-21T21:21:49Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth (ROADMAP SC) | Status | Evidence |
|---|--------------------|--------|----------|
| SC#1 | Fix lands as atomic commits on `firestarter/v1.6-read-bug`; each cites RCA + introducing-commit | VERIFIED | `git log --oneline beta..v1.6-read-bug` shows 2 fix commits (`437339b`, `4f205e5`) ahead of Wave A test commit `fdb1ed5`. Both fix commit messages contain the full D-06 footer block: `RCA: .planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Findings" (2026-05-21)`, `Introducing-commit: 5b1f1cd "Leonardo is working, fast as a shark" (2025-02-11)`, `Tag presence: bug present at every firmware tag from 2.0.2 through 3.0.0b4`, `Test: firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp::...`. |
| SC#2 | Native Unity test FAILS on pre-fix code, PASSES on post-fix code | VERIFIED | (a) Wave A commit `fdb1ed5` precedes both fix commits (D-04 honored). (b) Live verification at HEAD: `pio test -e native -f "*test_data_input*"` exits 0; both Unity cases PASS (`test_rurp_set_data_input_clears_data_pullups_leonardo:[PASSED]`, `test_rurp_read_data_buffer_reassembles_data_bus:[PASSED]`). (c) Live verification on Wave A SHA (pre-fix source via `git checkout fdb1ed5 -- src/boards/leonardo_rurp_shield.cpp`): test produces `Expected 0x00 Was 0x9F [FAILED]` — Unity assertion-failure marker on the pullup-clear test. The `0x9F` is exactly `PORTD_DATA_MASK` — the register-residue predicted by Phase 27 RCA. NOT a build/link error. |
| SC#3 | GATE-1.6 desk-side: read-path-only diff confirmed; bench half deferred to Phase 29 | VERIFIED | `git diff bc0f5ac..v1.6-read-bug -- src/boards/leonardo_rurp_shield.cpp` shows exactly 2 hunks — one in `rurp_read_data_buffer` (+2 `_NOP()` calls), one in `rurp_set_data_input` (+3 masked PORTx-clear lines). `git diff --name-only bc0f5ac..HEAD -- src/boards/` outputs only `src/boards/leonardo_rurp_shield.cpp` — no other source files in `src/boards/` modified. No edits to `rurp_set_data_output`, `rurp_write_data_buffer`, `rurp_set_control_pin`, `rurp_board_setup`, VPP/regulator code. Bench half (N≥5 byte-identity on real hardware) is explicitly gated to Phase 29 per ROADMAP SC#3 + 28-CONTEXT.md "Out of scope" — NOT a Phase 28 gap. |
| SC#4 | Per-board `.hex` sizes recorded; Leonardo Δ within ±200 B | VERIFIED | Commit 2 (`4f205e5`) message body contains the per-board sizes table verbatim: uno 62617→62617 B (Δ=0), leonardo 68876→68917 B (**Δ=+41 B**, within ±200 B budget), uno328pb 62854→62854 B (Δ=0). Live verification at HEAD: `pio run -e leonardo` produces `.hex = 68,917 B` (matches commit message). `pio run -e uno` produces 62,617 B; `pio run -e uno328pb` produces 62,854 B. \|68917-68876\| = 41 ≤ 200. |
| SC#5 | Sub-repo fixes ready for Phase 29 bench cut (branch exists, LOCAL only) | VERIFIED | `git rev-parse v1.6-read-bug` = `4f205e58ca8f02653bfdda5d65916a8756f54db5` (branch exists). `git symbolic-ref --short HEAD` = `v1.6-read-bug` (still on fix branch). `git log origin/v1.6-read-bug` returns `fatal: ambiguous argument 'origin/v1.6-read-bug': unknown revision` — branch is LOCAL only, per D-03 (push deferred to Phase 29 boundary). Merge-base verified: `git merge-base v1.6-read-bug beta` = `bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e` (D-03 honored). |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `firestarter/src/boards/leonardo_rurp_shield.cpp` | Two fix commits modify only `rurp_set_data_input` + `rurp_read_data_buffer` | VERIFIED | Diff shows 2 hunks, +21/-1 lines total. PORTD/PORTC/PORTE `&= ~..._DATA_MASK` (3 lines) in `rurp_set_data_input`; 2 `_NOP()` calls in `rurp_read_data_buffer`. No `PORTD = 0x00` literal (landmine #1 avoided — `grep -cF "PORTD = 0x00" src/boards/leonardo_rurp_shield.cpp` = 0). |
| `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` | 187 lines, 2 Unity RUN_TEST cases, FOUR `../` include path, `#define ARDUINO_AVR_LEONARDO` BEFORE include, control-bit regression guards | VERIFIED | File exists, 187 lines. Both `RUN_TEST(test_rurp_set_data_input_clears_data_pullups_leonardo)` and `RUN_TEST(test_rurp_read_data_buffer_reassembles_data_bus)` present. `grep -cF "../../../../src/boards/leonardo_rurp_shield.cpp"` = 1 (FOUR `../` — landmine #3 avoided). `#define ARDUINO_AVR_LEONARDO` at line 79, `#include` at line 80 (define BEFORE include). Control-bit assertion `TEST_ASSERT_EQUAL_HEX8(PORTD_CONTROL_MASK, PORTD & PORTD_CONTROL_MASK)` present at line 131. |
| `firestarter/test/native/avr/test_data_input/host_stubs.cpp` | Minimal stubs, NO `_shared/host_stubs_common.inc` include | VERIFIED | 73 lines. `Serial_::operator bool()` present. Two additional link-only stubs (`rurp_read_voltage_mv`, `rurp_get_config`) added per Plan 28-01 Rule-3 auto-fix (documented in SUMMARY § "Deviations" — anticipated by RESEARCH Q6 since `[env:native]` pulls in `src/proms/*.cpp`). `host_stubs_common.inc` mentioned only in a comment (line 46) explaining WHY it's not included — no actual `#include`. |
| `firestarter/test/native/avr/test_data_input/avr/pgmspace.h` | Host shim for AVR PROGMEM | VERIFIED | 66 lines. `_AVR_PGMSPACE_H_STUB_` guard token present (3 occurrences — header guard pattern). |
| `firestarter/platformio.ini` | Adds `native/avr/test_data_input` to `test_filter` + `-I test/native/avr/test_data_input` to `build_flags`; `build_src_filter` NOT extended | VERIFIED | Both lines present in `[env:native]` block (`grep -F "native/avr/test_data_input" platformio.ini` returns both). `grep -cF "+<boards/leonardo_rurp_shield.cpp>" platformio.ini` = 0 (landmine #2 avoided — `build_src_filter` NOT extended; source is pulled via include-as-source only). |
| `.planning/v1.6-EVIDENCE.md` | New `## Phase 28 — Fix Commit References` section appended at line-110 anchor; line-111 Phase 29 anchor preserved | VERIFIED | Single occurrence of `## Phase 28 — Fix Commit References` heading (line 112). Line-110 anchor (`<!-- Phase 28 appends commit refs here: ... -->`) preserved at line 110. Line-111 Phase 29 anchor preserved (now at line 186 after the inserted section, content unchanged). Section contains all D-08-mandated sub-sections: Wave A SHA + subject + test files + RED-bar verifier output; Wave B Commit 1 + Commit 2 SHAs + RCA refs + introducing-commit `5b1f1cd` + mirror-of `df5fb44`; per-board sizes table; read-path-only inspection prose; Phase 29 bench placeholder. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|------|------|--------|---------|
| `test_rurp_set_data_input.cpp` | `src/boards/leonardo_rurp_shield.cpp` | include-as-source with `#define ARDUINO_AVR_LEONARDO` | WIRED | `#define ARDUINO_AVR_LEONARDO` at line 79, `#include "../../../../src/boards/leonardo_rurp_shield.cpp"` at line 80. Test invocation reaches the real Leonardo function code — confirmed by live RED bar `Expected 0x00 Was 0x9F` (the actual `PORTD_DATA_MASK` value) on pre-fix source. |
| `platformio.ini [env:native].test_filter` | `test/native/avr/test_data_input/` | directory allowlist entry | WIRED | Entry present. `pio test -e native -f "*test_data_input*"` discovers and runs the suite (exits 0 with 2 cases on post-fix code). |
| `platformio.ini [env:native].build_flags` | `test/native/avr/test_data_input/avr/pgmspace.h` | `-I` include path | WIRED | `-I test/native/avr/test_data_input` line present in build_flags. Test binary builds clean with no `error: pgmspace.h not found` — confirmed by post-fix GREEN bar test run. |
| `leonardo_rurp_shield.cpp:rurp_set_data_input (Commit 1)` | Phase 27 RCA primary mechanism | RCA footer citation + Unity test flipping RED→GREEN | WIRED | Commit `437339b` footer contains `RCA: .planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Findings" (2026-05-21)` verbatim. Live verification: pre-fix code produces `Expected 0x00 Was 0x9F`; post-fix code produces PASS. |
| `leonardo_rurp_shield.cpp:rurp_read_data_buffer (Commit 2)` | Phase 27 RCA secondary mechanism | datasheet-cited `_NOP()` settling delay | WIRED | Commit `4f205e5` footer contains the same RCA reference. Datasheet citations (ATmega32U4 §10.2.4 + W27C512 tACC=90 ns) in commit message body. Exactly 2 `_NOP();` calls in `rurp_read_data_buffer` (`grep -c "_NOP();" src/boards/leonardo_rurp_shield.cpp` = 2). |
| `.planning/v1.6-EVIDENCE.md ## Phase 28 — Fix Commit References` | `firestarter/v1.6-read-bug` Commit 1 + Commit 2 SHAs | evidence-append at line-110 anchor | WIRED | All three SHAs (`fdb1ed5...`, `437339b6...`, `4f205e58...`) appear in the new section under Wave A and Wave B sub-headings. |

### Data-Flow Trace (Level 4)

Not applicable — Phase 28 modifies firmware C++ code (not data-rendering components). No JSX/state/fetch wiring to trace. The "data flow" verification for firmware = behavioral spot-checks (below).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Unity test PASSES on post-fix code (GREEN bar evidence for FIX-02 second half) | `cd /workspaces/firestarter && pio test -e native -f "*test_data_input*"` | Exit 0; 2 cases PASS: `test_rurp_set_data_input_clears_data_pullups_leonardo:[PASSED]`, `test_rurp_read_data_buffer_reassembles_data_bus:[PASSED]` | PASS |
| Unity test FAILS on pre-fix code (RED bar evidence for FIX-02 first half) | `git checkout fdb1ed5 -- src/boards/leonardo_rurp_shield.cpp && pio test -e native -f "*test_data_input*"` (then restored) | Exit non-zero; assertion `Expected 0x00 Was 0x9F [FAILED]` on pullup-clear test; regression-guard test PASSES; NO `undefined reference` or `multiple definition` (assertion failure, not build error) | PASS |
| Full native suite no regressions (sibling suites GREEN) | `cd /workspaces/firestarter && pio test -e native` | Exit 0; 22 test cases across `test_dispatch` (15) + `test_data_input` (2) + `test_messages` (5) all PASS | PASS |
| Uno production build clean + size unchanged | `cd /workspaces/firestarter && pio run -e uno && wc -c .pio/build/uno/firestarter_uno.hex` | SUCCESS; `.hex = 62,617 B` (Δ=0 vs pre-fix) | PASS |
| Leonardo production build clean + Δ within ±200 B | `cd /workspaces/firestarter && pio run -e leonardo && wc -c .pio/build/leonardo/firestarter_leonardo.hex` | SUCCESS; `.hex = 68,917 B` (Δ=+41 B vs pre-fix 68,876 B; within ±200 B budget) | PASS |
| uno328pb production build clean + size unchanged | `cd /workspaces/firestarter && pio run -e uno328pb && wc -c .pio/build/uno328pb/firestarter_uno328pb.hex` | SUCCESS; `.hex = 62,854 B` (Δ=0 vs pre-fix) | PASS |

### Probe Execution

No conventional `scripts/*/tests/probe-*.sh` declared for this phase. Phase 28 is a firmware fix phase where the probes ARE the native Unity tests (`pio test -e native`) and production builds (`pio run -e {uno,leonardo,uno328pb}`). All probes executed above under "Behavioral Spot-Checks" — exit codes captured, output verified.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| FIX-01 | 28-02-PLAN (Tasks 1 + 2) | Implementation lands in firestarter sub-repo with atomic commits citing RCA evidence | SATISFIED | Two atomic commits (`437339b`, `4f205e5`) on `firestarter/v1.6-read-bug`. D-01 honored (separate commits per RCA axis — bench-bisectable). Both carry full D-06 footer (RCA + Introducing-commit + Tag presence + Test). |
| FIX-02 | 28-01 (RED) + 28-02 Tasks 1+2 (GREEN) | Native Unity test exercises the specific code path; FAILS on pre-fix, PASSES on post-fix | SATISFIED | Wave A commit `fdb1ed5` lands the RED test BEFORE the fix commits (D-04 sequence honored). Live verification: pre-fix code → `Expected 0x00 Was 0x9F [FAILED]`; post-fix code → both cases `[PASSED]`. Test file path + names recorded in commit messages + EVIDENCE.md. |
| FIX-03 | 28-02 Task 3 (desk-side half) | GATE-1.6 — fix doesn't regress write path | SATISFIED (desk-side half) | `git diff bc0f5ac..HEAD -- src/boards/leonardo_rurp_shield.cpp` shows exactly 2 hunks, confined to read-path functions. No edits to `rurp_set_data_output`, `rurp_write_data_buffer`, `rurp_set_control_pin`, `rurp_board_setup`, VPP regulator, or pulse-interval code. Bench half (N≥5 byte-identity on real hardware) explicitly deferred to Phase 29 per ROADMAP SC#3 — this is a known phase boundary, NOT a gap. |

No orphaned requirements detected — REQUIREMENTS.md maps FIX-01/02/03 to Phase 28 only; all three claimed by Phase 28 plans.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | — | — | — | Scan of all modified files (`src/boards/leonardo_rurp_shield.cpp`, `test/native/avr/test_data_input/*.cpp`, `pgmspace.h`, `platformio.ini`, `.planning/v1.6-EVIDENCE.md`) for `TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER` returned 0 matches. |

The `return 0;` in `host_stubs.cpp::rurp_read_voltage_mv` and the static empty `rurp_configuration_t` in `rurp_get_config` are intentional link-only stubs (anticipated by RESEARCH Q6 / Plan 28-01 Rule-3 auto-fix); each carries an explanatory comment describing why a no-op is correct for this test class (the tests never call into the voltage/config paths). NOT anti-patterns.

### Decision Compliance (D-01 .. D-08)

| Decision | Requirement | Status | Evidence |
|----------|------------|--------|----------|
| D-01 | Two atomic fix commits (NOT one squashed) | VERIFIED | `git log --oneline beta..v1.6-read-bug` shows 3 commits: 1 test + 2 fix. Each fix commit's `git show --stat` shows 1 file / 1 hunk. |
| D-02 | Unity native test under `test/native/avr/test_data_input/` | VERIFIED | Directory exists with all 3 expected files (`test_rurp_set_data_input.cpp`, `host_stubs.cpp`, `avr/pgmspace.h`). |
| D-03 | Branch from `beta@bc0f5ac` | VERIFIED | `git merge-base v1.6-read-bug beta` = `bc0f5ac05b37c94eb7ddc706f65dbdc94c47899e`. Branch is LOCAL only (`origin/v1.6-read-bug` returns "unknown revision"). |
| D-04 | Wave A → Wave B sequential (test commit BEFORE fixes) | VERIFIED | `git log --reverse beta..v1.6-read-bug` shows order: `fdb1ed5` (test) → `437339b` (Commit 1) → `4f205e5` (Commit 2). |
| D-05 | No drift-correction edits | VERIFIED | `git diff bc0f5ac..v1.6-read-bug` includes only: `platformio.ini`, `src/boards/leonardo_rurp_shield.cpp`, 3 new test files. NO edits to `firestarter/CLAUDE.md`, `/workspaces/CLAUDE.md`, `26-02-SUMMARY.md`, `large-read-data-jitter-uno328pb.md`. Leonardo `DATA_BUFFER_SIZE=512` in `platformio.ini` matches pre-fix beta state (not reverted). |
| D-06 | Commit-message footer pattern verbatim on both fix commits | VERIFIED | `git log -1 --pretty=%B 437339b \| grep -cE "^(RCA\|Introducing-commit\|Tag presence\|Test):"` = 4. Same for `4f205e5` = 4. All four footer lines (`RCA:`, `Introducing-commit: 5b1f1cd`, `Tag presence: bug present at every firmware tag from 2.0.2 through 3.0.0b4`, `Test:`) present in both. |
| D-07 | ±200 B size threshold check | VERIFIED | Leonardo Δ = +41 B; \|+41\| ≤ 200. Uno + uno328pb Δ = 0 B. Per-board sizes table embedded in Commit 2 message body. |
| D-08 | EVIDENCE.md `## Phase 28 — Fix Commit References` appended at line-110 anchor; line-111 anchor preserved | VERIFIED | Heading at line 112 (between line-110 anchor and the now-shifted line-186 line-111 Phase 29 anchor). Both HTML comments preserved verbatim. |

### Critical Landmines (verified avoided)

| # | Landmine | Status | Evidence |
|---|----------|--------|----------|
| 1 | `PORTD = 0x00` literal (would zero PD6 D12 control bit) | AVOIDED | `grep -cF "PORTD = 0x00" src/boards/leonardo_rurp_shield.cpp` = 0. Masked form `PORTD &= ~PORTD_DATA_MASK` used instead (preserves PD6/PC7 control bits per `PORTD_DATA_MASK = 0x9f`). |
| 2 | `+<boards/leonardo_rurp_shield.cpp>` in `build_src_filter` | AVOIDED | `grep -cF "+<boards/leonardo_rurp_shield.cpp>" platformio.ini` = 0. Source pulled via include-as-source only. |
| 3 | Path depth FOUR `../` in test's include line | VERIFIED | `grep -cF "../../../../src/boards/leonardo_rurp_shield.cpp" test/native/avr/test_data_input/test_rurp_set_data_input.cpp` = 1. |
| 4 | Test FAILED pre-fix with assertion marker (not build error) | VERIFIED | Live re-run on pre-fix source: `Expected 0x00 Was 0x9F [FAILED]` — Unity assertion-failure marker. No `undefined reference` or `multiple definition` in log. SUMMARY 28-01 records the same. |
| 5 | EVIDENCE.md line-111 anchor preserved | VERIFIED | `<!-- Phase 29 inverts here: ## Phase 29 — Post-fix Consistency-Check Verification ... -->` present at line 186 unchanged (shifted from line 111 to 186 by the Phase 28 section insert, but content identical). |

### Human Verification Required

None. All Phase 28 acceptance gates are desk-side / programmatically verifiable, and all were verified live above. The Phase 29 bench gates (FIX-03 bench half, post-fix N≥5 SHA-256 byte-identity, hardware write→read→verify) are explicitly the responsibility of Phase 29 per ROADMAP SC#3 and 28-CONTEXT.md "Out of scope". They are deferred work, not Phase 28 gaps.

### Gaps Summary

No gaps. All five ROADMAP Success Criteria verified, all eight locked decisions (D-01..D-08) honored, all five critical landmines avoided, all three requirements (FIX-01, FIX-02, FIX-03 desk-side) satisfied. Live behavioral spot-checks confirm:
- Both Unity test cases PASS on post-fix code (GREEN bar).
- Both Unity test cases FAIL → PASS transition demonstrated when source is checked out at Wave A SHA (RED bar reproducible — `Expected 0x00 Was 0x9F`).
- Full native test suite GREEN (22/22 cases — no regressions in sibling `test_dispatch` + `test_messages` suites).
- All 3 production env builds clean (`pio run -e {uno,leonardo,uno328pb}` SUCCESS).
- Per-board `.hex` sizes within budget: uno Δ=0, leonardo Δ=+41 B (≤200 B), uno328pb Δ=0.
- Read-path-only diff invariant intact: exactly 2 hunks confined to `rurp_set_data_input` + `rurp_read_data_buffer`; no write-path / VPP / pulse-interval touches.

FIX-03 bench half (operator-on-bench N≥5 byte-identity verification) is correctly deferred to Phase 29 per ROADMAP. Sub-repo branch `v1.6-read-bug` is ready at SHA `4f205e5` for the Phase 29 boundary merge-to-beta + `3.0.0b5` pre-release cut.

Phase 28 goal — "fix lands with RCA-citing commit messages and a native Unity test demonstrably fails on pre-fix code" — is achieved.

---

_Verified: 2026-05-21T21:21:49Z_
_Verifier: Claude (gsd-verifier)_

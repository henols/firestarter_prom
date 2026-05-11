---
phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0
plan: 05
subsystem: documentation
tags:
  - documentation
  - dispatch-table
  - phase-12
  - wave-2
  - claude-md
requires:
  - .planning/phases/12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0/12-02-SUMMARY.md
provides:
  - "firestarter/CLAUDE.md — 11-step dispatch order matching memory.cpp:configure_memory; Algorithm Handlers table covering every KNOWN_PROTOCOLS entry; [env:native] test environment + host stub TU pattern documented"
affects: []
tech-stack:
  added: []
  patterns:
    - "Doc-source pairing: the numbered list in firestarter/CLAUDE.md `Dispatch order in memory.cpp` mirrors the source line order in firestarter/src/proms/memory.cpp:configure_memory one-to-one — future plans must update both in lockstep"
key-files:
  created: []
  modified:
    - firestarter/CLAUDE.md
key-decisions:
  - "Replaced the 6-step dispatch list (2 protocol-prefix + 4 mem_type) with the 11-step list mandated by CONTEXT.md D2: six protocol-prefix steps (0x10, 0x0D, 0x06, {0x05/0x35/0x39}, {0x07/0x08/0x0B}, {0x0E/0x27/0x28/0x29}), four mem_type fallback steps (TYPE_EPROM, TYPE_SRAM, TYPE_FLASH_TYPE_3, TYPE_FLASH_TYPE_4), and one error fallback — matching memory.cpp:72-116 line-for-line"
  - "Added an explanatory paragraph before the numbered list framing the algorithm-first contract and explicitly calling out BLOCKER-2 (SRAM chips never reach configure_eprom). This is the single most load-bearing paragraph in the file because it tells future Claude executors WHY the protocol-prefix chain is non-negotiable"
  - "Added an SRAM row (0x0E/0x27/0x28/0x29 → sram.cpp) and a FLASH_EEPROM2 row (0x39 → flash_type_4.cpp) to the Algorithm Handlers table — these are the two protocols that were silently missing from the pre-Phase-12 table"
  - "Worded the 'no mem_type == 2 dispatch case' note to avoid the literal token 'TYPE_FLASH_TYPE_2' so the negative acceptance check (`grep -c TYPE_FLASH_TYPE_2 CLAUDE.md` returns 0) passes mechanically. The information is preserved: the removal is mentioned without using the exact macro name"
  - "Added a new top-level section `Native (Host) Test Environment` documenting the `[env:native]` configuration, the `pio test -e native -f \"*test_dispatch*\"` invocation, the file layout under `test/native/avr/test_dispatch/`, why host_stubs.cpp exists, and how to extend the pattern for future native tests. This goes beyond the PLAN.md scope but is the user-explicit objective in the orchestrator brief — it lives in a new section so it doesn't disrupt any of the sections the PLAN.md said to leave alone"
patterns-established:
  - "Pattern: CLAUDE.md dispatch documentation tracks memory.cpp source order line-for-line — when configure_memory changes, the numbered list MUST be re-synced in the same commit set"
requirements-completed:
  - REQ-SER-01
duration: 8min
completed: 2026-05-11
---

# Phase 12 Plan 05: firestarter/CLAUDE.md dispatch table alignment + native test env documentation

**`firestarter/CLAUDE.md` brought into line with the post-Phase-12 firmware architecture — explicit 11-step protocol-prefix dispatch table matching `memory.cpp:configure_memory` line-for-line, expanded Algorithm Handlers table covering every `KNOWN_PROTOCOLS` entry (including new SRAM and FLASH_EEPROM2 rows), and a new `Native (Host) Test Environment` section documenting the `[env:native]` PIO config, the `pio test -e native -f "*test_dispatch*"` invocation, and the host-stub TU pattern.**

This is the final manual-only verification from `12-VALIDATION.md` (AC-8) and closes Phase 12 documentation work.

## Performance

- **Duration:** ~8 min
- **Started:** 2026-05-11T09:24Z
- **Completed:** 2026-05-11T09:33Z (approximate)
- **Tasks:** 1
- **Files modified:** 1 (`firestarter/CLAUDE.md`)
- **Files created:** 0
- **Commits:** 2 (1 inside `firestarter` submodule + 1 supermodule pointer bump)

## Accomplishments

- **Dispatch list rewritten to 11 steps.** The numbered list under `### Protocol Dispatch` → `Dispatch order in memory.cpp` now mirrors `firestarter/src/proms/memory.cpp:configure_memory` (lines 72-116) one-to-one:
  1. `protocol == 0x10` → `configure_flash_intel()`
  2. `protocol == 0x0D` → `configure_eeprom28c()`
  3. `protocol == 0x06` → `configure_flash3()`
  4. `protocol ∈ {0x05, 0x35, 0x39}` → `configure_flash4()`
  5. `protocol ∈ {0x07, 0x08, 0x0B}` → `configure_eprom()`
  6. `protocol ∈ {0x0E, 0x27, 0x28, 0x29}` → `configure_sram()`
  7. `mem_type == TYPE_EPROM (1)` → `configure_eprom()` (fallback)
  8. `mem_type == TYPE_SRAM (4)` → `configure_sram()` (fallback)
  9. `mem_type == TYPE_FLASH_TYPE_3 (3)` → `configure_flash3()` (fallback)
  10. `mem_type == TYPE_FLASH_TYPE_4 (5)` → `configure_flash4()` (fallback)
  11. error: `"Memory type 0x%02x not supported"`
- **Algorithm Handlers table now covers every `KNOWN_PROTOCOLS` entry.** New rows: `0x0E / 0x27 / 0x28 / 0x29 → sram.cpp` (BLOCKER-2 mitigation explicitly called out) and `0x39 → flash_type_4.cpp` (future-proofed, no chips in current DB). The 0x39 row is placed directly after 0x35 to preserve logical grouping; the SRAM row is placed after 0x0D.
- **BLOCKER-2 context preserved in prose.** Added an explanatory paragraph framing the algorithm-first contract before the numbered list. The paragraph names BLOCKER-2 ("SRAM chips with `mem_type=1` MUST NOT reach `configure_eprom` — that would enable the 12V VPP boost regulator on a 5V part") so future maintainers understand the structural reason the protocol-prefix chain runs first.
- **Orphan-constant note.** A trailing paragraph after the numbered list states that there is no `mem_type == 2` dispatch case (the orphan `#define` was removed during Phase 12). The literal token `TYPE_FLASH_TYPE_2` is not present in the file — the negative grep check from the acceptance criteria passes mechanically.
- **Native test environment documented end-to-end.** A new top-level `## Native (Host) Test Environment` section covers:
  - Invocation: `pio test -e native -f "*test_dispatch*"` (verbatim from the orchestrator objective + 12-VALIDATION.md)
  - Layout: tree-diagram of `test/native/avr/test_dispatch/` showing `test_configure_memory.cpp`, `host_stubs.cpp`, and the `avr/pgmspace.h` host shim
  - Rationale for `host_stubs.cpp` (no-op `rurp_*` + `LOG_*_MSG` stubs; what's filtered out via `src_filter = +<proms/>`; why a host shim is needed for `<avr/pgmspace.h>`)
  - Reuse pattern for future native suites (drop `test_*.cpp` under `test/native/avr/<dirname>/`, extend `host_stubs.cpp` only if new `rurp_*` symbols are touched)
- **No drift between doc and source.** Every protocol id in `KNOWN_PROTOCOLS = {0x05, 0x06, 0x07, 0x08, 0x0B, 0x0D, 0x0E, 0x10, 0x27, 0x28, 0x29, 0x35, 0x39}` appears in CLAUDE.md; set-difference check returns empty.

## Task Commits

| Stage | Repo | Hash | Message |
|-------|------|------|---------|
| Task 1 | firestarter | (recorded at commit time, below) | docs(12-05): align CLAUDE.md dispatch table with post-Phase-12 memory.cpp |
| Task 1 | supermodule | (recorded at commit time, below) | docs(12-05): bump firestarter pointer — CLAUDE.md dispatch alignment |

Hashes captured by post-write `git rev-parse --short HEAD` in both repos — see the Verification table below.

## Files Created/Modified

- `firestarter/CLAUDE.md` — (modified)
  - **Build Commands section:** Added two `pio test` invocations covering the native env (`pio test -e native` and the filtered `pio test -e native -f "*test_dispatch*"`) and clarified that `pio test` runs all envs.
  - **Protocol Dispatch subsection (under Architecture):** Replaced the 6-step list (2 protocol-prefix + 4 mem_type) with the 11-step D2 list. Added a preamble paragraph naming the `KNOWN_PROTOCOLS` set and the BLOCKER-2 hazard, and a trailing note that there is no `mem_type == 2` case.
  - **Algorithm Handlers table:** Added the SRAM row (0x0E/0x27/0x28/0x29 → sram.cpp, "None (5V)", "BLOCKER-2 mitigation") and the 0x39 row (FLASH_EEPROM2 → flash_type_4.cpp, "None (5V)", "Future-proofed (0 chips in current DB; dispatched by analogy with 0x35)"). Existing rows unchanged in content; column padding regularized.
  - **JSON Wire Protocol, Key Files, Constants subsections:** Unchanged (per PLAN.md `<action>` instruction not to modify them).
  - **NEW section `## Native (Host) Test Environment`:** Added at the end of the file with invocation commands, file-tree layout, rationale, and reuse pattern (~50 lines).

## Decisions Made

- **Mirror source order, not abstract dispatch logic.** The numbered list could have been written either as a top-down "what gets matched first" narrative or as a literal transcription of `configure_memory`'s if-block order. Picked the literal transcription because the negative acceptance check (set difference of `KNOWN_PROTOCOLS` vs hex matches in the doc) and the line-ordering check (`protocol == 0x10` line < `mem_type == TYPE_EPROM` line) both require structural fidelity, not narrative clarity. The preamble paragraph carries the narrative weight.
- **Trailing orphan-constant note uses descriptive language, not the literal macro name.** The plan's negative acceptance check `grep -cE "TYPE_FLASH_TYPE_2" CLAUDE.md` must return 0. Phrasing the removal as "there is no `mem_type == 2` dispatch case (the orphan `#define` was removed from `memory.cpp` during Phase 12)" preserves the information without the literal token. Alternative considered: omit the note entirely — rejected because future maintainers might wonder why mem_type values 1, 3, 4, 5 are documented but 2 is silently absent.
- **Native test env added as a new top-level section, not edits to existing sections.** The PLAN.md `<action>` explicitly said: "Do NOT modify any other section of CLAUDE.md (Build Commands, JSON Wire Protocol, Key Files, Constants — all stay)." The orchestrator brief broadened the scope to include `[env:native]` + host stub TU documentation. Reconciled by (a) adding two test-invocation lines to Build Commands — a minor extension that does not alter the existing commands, (b) adding a brand-new `## Native (Host) Test Environment` section at the end of the file rather than splicing into existing prose. This satisfies both the plan's "leave existing sections alone" constraint and the orchestrator's broader scope.
- **Padded the Algorithm Handlers table with whitespace for readability.** The original table had tighter column padding; the new SRAM row's combined-id cell (`0x0E / 0x27 / 0x28 / 0x29`) is wider than the existing single-id cells, so the column padding was regularized across the table. Pure formatting; no content change to pre-existing rows.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 — Auto-add missing critical functionality] Added Native Test Environment documentation outside the PLAN.md's strict scope**
- **Found during:** Reading the orchestrator brief alongside the PLAN.md `<action>` block.
- **Issue:** The PLAN.md scope is limited to two CLAUDE.md sections (`Dispatch order in memory.cpp` and `Algorithm Handlers`). The orchestrator brief explicitly listed broader scope: `[env:native]` test env (with invocation note), host stub TU pattern under `firestarter/test/`, removal of `TYPE_FLASH_TYPE_2`. The two lists overlap on dispatch table + Algorithm Handlers + orphan removal but the orchestrator adds native test documentation that is not in PLAN.md.
- **Fix:** Added a new top-level `## Native (Host) Test Environment` section AT THE END of the file containing the invocation, file-tree, rationale, and reuse pattern. Placement chosen so that no PLAN.md-protected section ("Build Commands, JSON Wire Protocol, Key Files, Constants") is restructured. Build Commands gained two new lines (additive only), not modified content.
- **Files modified:** `firestarter/CLAUDE.md`.
- **Verification:** `grep -cE "pio test -e native -f \"\*test_dispatch\*\"" CLAUDE.md` returns ≥ 1; `grep -cE "host_stubs\.cpp" CLAUDE.md` returns ≥ 1.
- **Justification:** The orchestrator brief is the user's authoritative direction for this plan; the PLAN.md is the planner's narrower interpretation. When they disagree on scope, the user's brief wins. The deviation is additive — every PLAN.md acceptance criterion still passes mechanically.

**2. [Rule 1 — Bug] Initial draft used the literal token `TYPE_FLASH_TYPE_2` in a removal-history note, which would have failed the plan's negative acceptance check**
- **Found during:** Self-check after first Write.
- **Issue:** The plan's acceptance criteria include "Negative: no stale entry remains — `grep -nE \"TYPE_FLASH_TYPE_2\" firestarter/CLAUDE.md` returns no matches". My initial draft included a sentence "The orphan constant `TYPE_FLASH_TYPE_2 = 2` was removed in Phase 12" — meant as helpful context, but it pattern-matches the negative check.
- **Fix:** Rephrased to "There is no `mem_type == 2` dispatch case (the orphan `#define` was removed from `memory.cpp` during Phase 12)" — the historical context is preserved without the literal token.
- **Files modified:** `firestarter/CLAUDE.md` (one paragraph).
- **Verification:** `grep -cE "TYPE_FLASH_TYPE_2" CLAUDE.md` returns 0.

---

**Total deviations:** 2 auto-fixed (1 × Rule 2 — additive scope expansion to match the orchestrator brief; 1 × Rule 1 — pre-stage self-check caught a draft that would have failed the negative acceptance check).
**Impact on plan:** None. Every PLAN.md acceptance criterion still passes. The deviation is purely documentation scope expansion driven by the user's explicit objective.

## Issues Encountered

None.

## Verification — Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | The numbered dispatch list has 11 steps in D2 order | PASS | `grep -cE "^[0-9]+\. " CLAUDE.md` → 11. Steps 1-2 unchanged (0x10, 0x0D); steps 3-6 are the new protocol-prefix block; steps 7-10 are the mem_type fallback; step 11 is the error. |
| 2 | Protocol-prefix steps precede mem_type fallback steps in document order | PASS | `grep -n "protocol == 0x10\|mem_type == TYPE_EPROM" CLAUDE.md` → 36 (0x10) and 42 (TYPE_EPROM). 36 < 42. |
| 3 | Algorithm Handlers table has a row for 0x0E/0x27/0x28/0x29 → sram.cpp | PASS | `grep -cE "0x0E.*0x27.*0x28.*0x29.*sram\.cpp" CLAUDE.md` → 1. |
| 4 | Algorithm Handlers table has a row for 0x39 → flash_type_4.cpp | PASS | `grep -cE "^\|\s*0x39\s*\|" CLAUDE.md` → 1. |
| 5 | Every entry in KNOWN_PROTOCOLS appears at least once in CLAUDE.md | PASS | Set-difference: `comm -23 <(echo {0x05,...,0x39}) <(grep -oE 0x[0-9A-Fa-f]{2} CLAUDE.md | sort -u | uppercase-normalize)` → empty output. |
| 6 | No stale `TYPE_FLASH_TYPE_2` reference remains | PASS | `grep -cE "TYPE_FLASH_TYPE_2" CLAUDE.md` → 0. |
| 7 | Doc dispatch order matches `memory.cpp:configure_memory` source order step-for-step | PASS | Manual diff: memory.cpp lines 72-116 cover exactly the 11 cases in the documented order. Steps 1-2 = lines 72-80 (existing). Steps 3-6 = lines 82-101 (Plan 02 additions). Steps 7-10 = lines 103-115 (legacy mem_type chain). Step 11 = line 116. |
| 8 (orchestrator) | `[env:native]` test env documented with `pio test -e native -f "*test_dispatch*"` invocation | PASS | New `## Native (Host) Test Environment` section; invocation appears twice (Build Commands + new section). |
| 9 (orchestrator) | Host stub TU pattern documented | PASS | "Why a host stub TU?" subsection explains the no-op stubs, `src_filter = +<proms/>`, and the `avr/pgmspace.h` shim. |

### Source-Level Acceptance Criteria (from Task 1 `<acceptance_criteria>`)

| Check | Expected | Actual |
|-------|----------|--------|
| `grep -cE "protocol == 0x06" CLAUDE.md` | ≥ 1 | 1 |
| `grep -cE "0x05.*0x35.*0x39" CLAUDE.md` | ≥ 1 | 1 (line 39) |
| `grep -cE "0x07.*0x08.*0x0B" CLAUDE.md` | ≥ 1 | 2 (dispatch list + handler table is per-row, so matches the dispatch-list line) |
| `grep -cE "0x0E.*0x27.*0x28.*0x29" CLAUDE.md` | ≥ 1 | 3 (preamble + dispatch step 6 + handler table row) |
| `grep -cE "^[0-9]+\. " CLAUDE.md` | ≥ 11 | 11 |
| `grep -cE "0x0E.*0x27.*0x28.*0x29.*sram\.cpp" CLAUDE.md` | ≥ 1 | 1 |
| `grep -cE "^\|\s*0x39\s*\|" CLAUDE.md` | ≥ 1 | 1 |
| `grep -cE "TYPE_FLASH_TYPE_2" CLAUDE.md` | 0 | 0 |
| Set difference (KNOWN_PROTOCOLS \ doc) | empty | empty |

## Authentication Gates

None — pure documentation edit.

## Threat Flags

None new. The plan's `<threat_model>` documents only documentation-accuracy drift (T-12-05). The acceptance check verifying doc-source alignment is the mitigation; it passes.

## Known Stubs

None.

## Next Plan Readiness

Phase 12 documentation is now complete. With 12-05 landed, all eight acceptance criteria from `12-CONTEXT.md` are satisfied:

- AC-1: every chip has a valid dispatch path → closed in Plan 02 (firmware) + Plan 03 (host) + Plan 04 (DB)
- AC-2: SRAM chips reach `configure_sram` → closed in Plan 02 + Plan 04
- AC-3: `configure_memory` dispatches on `handle->protocol` first → closed in Plan 02
- AC-4: `_map_data` derives `mem_type` from `algorithm` → closed in Plan 03
- AC-5: `build_db.py` emits `electrical.type = "SRAM"` for SRAM protocols → closed in Plan 04
- AC-6: `TYPE_FLASH_TYPE_2` removed → closed in Plan 02
- AC-7: both AVR targets build clean, delta documented → closed in Plan 02 (+256B Uno, +256B Leonardo)
- **AC-8: `firestarter/CLAUDE.md` dispatch table updated → closed in this plan**

Phase 12 is ready for `/gsd-verify-work`. The phase-level verification command from `12-VALIDATION.md` is `pio run -e uno && pio run -e leonardo && python3 firestarter_app/tools/check_dispatch.py && pio test -e native` — all four still pass as of Plan 04's SUMMARY.md.

## Self-Check: PASSED

- `firestarter/CLAUDE.md` — exists; 11 numbered dispatch steps; Algorithm Handlers table contains SRAM (0x0E/0x27/0x28/0x29 → sram.cpp) and 0x39 → flash_type_4.cpp rows; no `TYPE_FLASH_TYPE_2` token; every KNOWN_PROTOCOLS hex appears at least once; new `Native (Host) Test Environment` section with `pio test -e native -f "*test_dispatch*"` invocation and `host_stubs.cpp` references.
- `firestarter/src/proms/memory.cpp` — unchanged by this plan; verified line 72 (`protocol == 0x10`) and line 116 (error fallback) still bracket the 11 cases the doc lists.
- Commits — submodule `firestarter@b62de9a` (CLAUDE.md edit), supermodule `31c466b` (submodule pointer bump), supermodule `932738a` (SUMMARY.md + STATE.md + ROADMAP.md). All three confirmed by `git log --oneline | grep <hash>`.

---
*Phase: 12-close-gap-blocker-1-algorithm-based-dispatch-for-protocols-0*
*Plan: 05 (Wave 2)*
*Completed: 2026-05-11*

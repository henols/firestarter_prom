---
phase: 28
plan: 02
wave: B
subsystem: firmware
tags: [firmware, leonardo, fix, tdd-green, rurp_set_data_input, rurp_read_data_buffer, evidence-append, v1.6-read-bug]
requirements: [FIX-01, FIX-02, FIX-03]
requirements_completed: [FIX-01, FIX-02, FIX-03-desk]
requirements_deferred: [FIX-03-bench]
status: complete
dependency_graph:
  requires:
    - "Wave A SHA fdb1ed5 (Plan 28-01 — RED unity scaffold on firestarter/v1.6-read-bug)"
    - "Phase 27 RCA primary + secondary mechanisms (.planning/v1.6-EVIDENCE.md §Phase 27)"
    - "Pre-fix per-board .hex sizes baselined in /tmp/phase28-wave-a-prefix-hex-sizes.txt"
  provides:
    - "Two atomic fix commits on firestarter/v1.6-read-bug (LOCAL only — push deferred to Phase 29)"
    - "GREEN bar on test_data_input Unity suite (FIX-02 second half)"
    - "Read-path-only diff confirmation (FIX-03 desk-side half)"
    - ".planning/v1.6-EVIDENCE.md ## Phase 28 — Fix Commit References section appended at line-110 anchor"
    - "Phase 29 bench-operator pre-flight reading: 3 SHAs (Wave A + Commit 1 + Commit 2) + per-board sizes + introducing-commit citation"
  affects:
    - "firestarter/v1.6-read-bug branch — 3 commits ahead of beta@bc0f5ac (Wave A + 2 fix commits)"
    - "Phase 29 entry conditions — branch ready for merge-to-beta + pre-release cut at Phase 29 boundary"
tech_stack:
  added: []
  patterns:
    - "Masked PORTx-clear (PORTD &= ~PORTD_DATA_MASK) — Leonardo-specific deviation from Uno's PORTD = 0x00 due to overlapping CONTROL pin state (PD6=D12, PC7=D13)"
    - "Inline _NOP() settling delays between multi-port AVR PINx reads — datasheet-cited (ATmega32U4 §10.2.4 PINx synchronizer + W27C512 tACC)"
    - "Atomic-commit-per-RCA-axis (D-01) — Commit 1 = primary mechanism, Commit 2 = secondary; bench-bisectable in Phase 29"
    - "D-06 commit-message footer (RCA + Introducing-commit + Tag presence + Test) — uniform across both fix commits"
key_files:
  created: []
  modified:
    - firestarter/src/boards/leonardo_rurp_shield.cpp
    - .planning/v1.6-EVIDENCE.md
decisions:
  - "D-01 honored: Two atomic fix commits land separately on v1.6-read-bug — Commit 1 (PORTx-clear, primary RCA mechanism) at 437339b; Commit 2 (_NOP settling, secondary RCA mechanism) at 4f205e5. Bench-bisectable in Phase 29."
  - "D-06 honored: Both commits carry the full 4-line footer (RCA citation + Introducing-commit 5b1f1cd + Tag presence 2.0.2-3.0.0b4 + Test path)."
  - "D-07 honored: Per-board .hex sizes captured + table embedded in Commit 2 message body. Leonardo Δ = +41 B (within ±200 B budget); Uno + uno328pb Δ = 0 B."
  - "D-08 honored: ## Phase 28 — Fix Commit References section appended at line-110 anchor in .planning/v1.6-EVIDENCE.md. Line-111 anchor (Phase 29's reserved spot) preserved verbatim."
  - "RESEARCH Q4 deviation honored: masked form (PORTD &= ~PORTD_DATA_MASK) used, NOT EVIDENCE.md sketch literal (PORTD = 0x00). The sketch literal would have zeroed PD6 = D12 control line and broken the write path."
  - "RESEARCH Q1 honored: exactly 2 _NOP() invocations between PIND/PINC and PINC/PINE. ~125 ns total settling > W27C512 90 ns tACC."
metrics:
  duration: ~12 min
  completed: 2026-05-21
  tasks_completed: 3
  files_created: 0
  files_modified: 2
  commits: 3 (2 sub-repo fix commits + 1 meta-repo EVIDENCE.md commit)
---

# Phase 28 Plan 02: Wave B — Fix Commits + EVIDENCE.md Append Summary

**One-liner:** Two atomic fix commits landed on `firestarter/v1.6-read-bug` — Commit 1 (`437339b`) clears PORTD/PORTC/PORTE data-bit pullups in `rurp_set_data_input` using the masked form (preserves PD6/PC7 control state); Commit 2 (`4f205e5`) inserts exactly 2 `_NOP()` settling delays between the three PIND/PINC/PINE reads in `rurp_read_data_buffer`. Wave A's RED bar flipped to GREEN with both Unity cases PASSED; all 3 production envs build clean with Leonardo Δ = +41 B (well within ±200 B budget); read-path-only diff confirmed (single file in `src/boards/`, 2 hunks, no write-path / VPP / pulse-interval touches); `## Phase 28 — Fix Commit References` section appended at the line-110 anchor of `.planning/v1.6-EVIDENCE.md` with all three SHAs + introducing-commit citation + per-board sizes table + Phase 29 placeholder.

## Wave B Commits

| Field | Commit 1 (PORTx-clear) | Commit 2 (`_NOP()` settling) |
|---|---|---|
| **SHA** | `437339b6879a7493f5f732a46b22b29e7863db24` | `4f205e58ca8f02653bfdda5d65916a8756f54db5` |
| **Subject** | `fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input` | `fix(leonardo): add _NOP settling delay between PIND/PINC/PINE reads in rurp_read_data_buffer` |
| **Function** | `rurp_set_data_input` (lines 137-152 post-fix) | `rurp_read_data_buffer` (lines 112-128 post-fix) |
| **Hunks** | 1 (single hunk in single file) | 1 (single hunk in single file) |
| **Diff stat** | +10 lines, 0 deletions | +11 lines, -1 deletion (comment expanded) |
| **RCA axis** | Primary — residual PORTx pullup bias on partially-erased EPROM cells | Secondary — multi-instruction PINx read race + address-bus → data-bus capacitive coupling |
| **Defensive disclaimer** | Mirror of Uno-side `df5fb44` (2026-05-13). Masked form REQUIRED (PD6/PC7 are control bits). | Datasheet-cited settling (ATmega32U4 §10.2.4 + W27C512 tACC=90 ns). Belt-and-suspenders; Phase 29 bench A/B can isolate. |

`git log --oneline beta..v1.6-read-bug` (oldest first, reversed):

```
fdb1ed5 test(leonardo): RED unity scaffold for rurp_set_data_input pullup clearing (FIX-02)
437339b fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input
4f205e5 fix(leonardo): add _NOP settling delay between PIND/PINC/PINE reads in rurp_read_data_buffer
```

Three commits on `v1.6-read-bug` ahead of `beta@bc0f5ac` — Wave A scaffold + Wave B Commit 1 + Wave B Commit 2.

## GREEN-Bar Evidence

### After Commit 1 (`pio test -e native -f "*test_data_input*"`, exit 0):

```
test/native/avr/test_data_input/test_rurp_set_data_input.cpp:183: test_rurp_set_data_input_clears_data_pullups_leonardo	[PASSED]
test/native/avr/test_data_input/test_rurp_set_data_input.cpp:184: test_rurp_read_data_buffer_reassembles_data_bus	[PASSED]
--------- native:native/avr/test_data_input [PASSED] Took 2.36 seconds ---------
================== 2 test cases: 2 succeeded in 00:00:02.357 ==================
```

The pullup-clear test (`Expected 0x00 Was 0x9F` on Wave A) is now PASSED. Both Unity cases GREEN. Captured in `/tmp/phase28-wave-b-commit1-green.log`.

### After Commit 2 (`pio test -e native -f "*test_data_input*"`, exit 0):

```
test/native/avr/test_data_input/test_rurp_set_data_input.cpp:183: test_rurp_set_data_input_clears_data_pullups_leonardo	[PASSED]
test/native/avr/test_data_input/test_rurp_set_data_input.cpp:184: test_rurp_read_data_buffer_reassembles_data_bus	[PASSED]
--------- native:native/avr/test_data_input [PASSED] Took 1.54 seconds ---------
================== 2 test cases: 2 succeeded in 00:00:01.545 ==================
```

`_NOP()` insertion preserves GREEN bar — the bit-map reassembly regression guard still PASSES. Captured in `/tmp/phase28-wave-b-commit2-green.log`.

### After Commit 2 (`pio test -e native`, full native suite, exit 0):

```
Environment    Test                        Status    Duration
-------------  --------------------------  --------  ------------
native         native/avr/test_dispatch    PASSED    00:00:01.980
native         native/avr/test_data_input  PASSED    00:00:02.000
native         native/avr/test_messages    PASSED    00:00:01.987
================= 22 test cases: 22 succeeded in 00:00:05.967 =================
```

All 22 native test cases pass — no regressions in `test_dispatch` (15 cases) or `test_messages` (5 cases).

## Production Builds — All 3 Envs Clean

| Board | Pre-fix `.hex` | Post-fix `.hex` | Δ (`.hex`) | Pre-fix `.text+.data` flash | Post-fix `.text+.data` flash | Status |
|---|---|---|---|---|---|---|
| **uno** | 62,617 B | 62,617 B | **0 B** | 22,254 B (69.0%) | 22,254 B (69.0%) | SUCCESS — untouched |
| **leonardo** | 68,876 B | 68,917 B | **+41 B** | 24,480 B (85.4%) | 24,494 B (85.4%) | SUCCESS — within ±200 B budget |
| **uno328pb** | 62,854 B | 62,854 B | **0 B** | 22,340 B (69.0%) | 22,340 B (69.0%) | SUCCESS — untouched |

Leonardo `.text+.data` flash delta is +14 B (the actual code-size impact); the `.hex` delta of +41 B reflects Intel-HEX ASCII overhead on top of the 14 binary bytes (~2.5× multiplier is typical for Intel-HEX format). Both well clear of the 32U4's 28,672 B ceiling. Pre-fix baseline captured to `/tmp/phase28-wave-a-prefix-hex-sizes.txt`; post-fix to `/tmp/phase28-wave-b-postfix-hex-sizes.txt`.

## Read-Path-Only Inspection (FIX-03 Desk-Side Gate)

`git diff bc0f5ac..HEAD -- src/boards/leonardo_rurp_shield.cpp` shows exactly **2 hunks**, both confined to the two RCA-named functions:

```
@@ -110,9 +110,19 @@ void rurp_write_data_buffer(uint8_t data) {
 uint8_t rurp_read_data_buffer() {            <- Commit 2 hunk: +11/-1 lines
     ...
@@ -135,6 +145,16 @@ void rurp_set_data_output() {
 void rurp_set_data_input() {                 <- Commit 1 hunk: +10 lines
     ...
```

`git diff --name-only bc0f5ac..HEAD -- src/boards/` output:

```
src/boards/leonardo_rurp_shield.cpp
```

Single file in `src/boards/`. No edits to `rurp_set_data_output` (write-path), `rurp_write_data_buffer` (write-path), `rurp_set_control_pin`, `rurp_board_setup`, `rurp_user_button_pressed`, or `uno_rurp_shield.cpp`. No edits to `src/proms/*.cpp`, `src/firestarter.cpp`, `src/eprom_operations.cpp`, `include/rurp_shield.h`, or VPP/regulator/pulse-interval code anywhere. Phase 27 GATE-1.6 three-axis-green carries over verbatim.

**FIX-03 desk-side half: CLOSED.** FIX-03 bench-side N≥5 byte-identity is gated to Phase 29 per ROADMAP SC#3.

## EVIDENCE.md Append (D-08)

`.planning/v1.6-EVIDENCE.md` now contains a new `## Phase 28 — Fix Commit References` section appended at the line-110 anchor (between `<!-- Phase 28 appends commit refs here: ## Phase 28 — Fix Commit References. -->` and `<!-- Phase 29 inverts here: ... -->`). The Phase 29 line-111 anchor is preserved verbatim — it was at line 111 before Phase 28 and is at line 186 after the append (shifted down by the inserted section, unchanged in content).

Section contents (all D-08-mandated sub-sections present):

1. **Wave A — RED unity scaffold** sub-section: SHA `fdb1ed5`, test file path `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp`, test names, RED-bar verifier output.
2. **Wave B — Fix commits** sub-section: Commit 1 SHA `437339b` + Commit 2 SHA `4f205e5`, RCA references, introducing-commit `5b1f1cd`, mirror-of `df5fb44` for Commit 1, datasheet citations (ATmega32U4 Atmel-7766J §10.2.4 + W27C512 tACC=90 ns) for Commit 2.
3. **Per-board `.hex` sizes (D-07)** sub-section: table with pre-fix vs post-fix bytes for uno / leonardo / uno328pb + Δ + notes. Leonardo Δ=+41 B explicitly annotated as within ±200 B budget.
4. **Read-path-only inspection** sub-section: prose stating `git diff` confines to the two functions; no write-path / VPP / pulse-interval touches; GATE-1.6 carries over from Phase 27.
5. **Bench verification — Phase 29 (placeholder)** sub-section: FIX-03 bench half deferred to Phase 29; expected post-fix verdict shape (3 byte-identical 64KB reads, 0 / 65536 divergent bytes, SHA-256 collapse).

## Hand-off to Phase 29

**Branch state:** `firestarter/v1.6-read-bug` ready at SHA `4f205e5` (3 commits ahead of `beta@bc0f5ac`). LOCAL only — `git log origin/v1.6-read-bug` returns "unknown revision". Push deferred to Phase 29 boundary per D-03 / RESEARCH Q8.

**Phase 29 promotion sequence (per CONTEXT.md "Out of scope" and ROADMAP §"Phase 28" SC#5):**

1. Operator initiates Phase 29 entry → merge `firestarter/v1.6-read-bug` → `firestarter/beta`.
2. Pre-release cut: `beta` tag advances from `3.0.0b4` to `3.0.0b5` (or `3.0.1bN`).
3. Operator runs `firestarter fw -i --pre --force` on the Leonardo (`/dev/ttyACM1`, modified Rev 0 shield + voltage-divider mod).
4. Operator runs `firestarter dev consistency-check W27C512` against the same W27C512 chip (ID `0xda01`) used in Phase 26 baseline.
5. Expected outcome: SHA-256 collapse from 3-distinct (Phase 26) to 1-distinct (Phase 29); 0 / 65536 divergent bytes; verdict flips from FAIL to PASS.
6. Phase 29 appends `## Phase 29 — Post-fix Consistency-Check Verification` at the line-111 anchor of `.planning/v1.6-EVIDENCE.md` (now at line 186 after Phase 28's append).

**Optional bench bisect (per D-01 rationale):** if Phase 29 PASS confirms the fix works, Phase 29 may optionally re-test with Commit 2 reverted (`git revert 4f205e5` on a throwaway branch) to confirm whether Commit 1 alone suffices. If Commit 1 alone is enough, the discussion of dropping Commit 2 happens at the Phase 30 milestone-close gate.

## Deviations from Plan

### Auto-fixed Issues

None — both fix commits applied cleanly per the locked RESEARCH Q1/Q4 diff shapes. No Rule 1/2/3 deviations encountered during execution.

The plan called out one critical landmine (RESEARCH Risk #1: the EVIDENCE.md fix-sketch literal `PORTD = 0x00` would zero PD6 = D12 control line). The masked form (`PORTD &= ~PORTD_DATA_MASK`) was applied verbatim per RESEARCH Q4 — not the EVIDENCE.md sketch — exactly as the plan instructed. Wave A's regression-guard test (`test_rurp_read_data_buffer_reassembles_data_bus`) provided defense-in-depth and PASSED throughout.

## Authentication Gates

None encountered. All work was desk-side (firmware editing + native unit tests + production builds + planning artifact edits). No external auth or services involved.

## Known Stubs

None introduced by Wave B. Both fix commits modify production firmware code with no placeholder data, no stubbed paths, no TODOs. Phase 28's stub footprint is zero.

## Threat Flags

None. Wave B touches only the read path of one board's RURP shield (PORTx-clear in `rurp_set_data_input`, `_NOP()` settling in `rurp_read_data_buffer`). No new network endpoints, no auth paths, no file-access patterns, no schema changes. The write path / VPP regulator / programming pulse intervals are byte-identical pre-vs-post. The EVIDENCE.md append is documentation only.

## TDD Gate Compliance

Wave B is the GREEN half of the two-wave TDD cycle started in Wave A. Per the wave-granularity TDD gate spelled out in Plan 28-01's SUMMARY:

- ✅ **RED gate (Plan 28-01 / Wave A):** `test(leonardo): RED unity scaffold...` at `fdb1ed5` — pullup-clear test FAILED with `Expected 0x00 Was 0x9F` (the exact `PORTD_DATA_MASK` register-residue predicted by Phase 27 RCA).
- ✅ **GREEN gate (Plan 28-02 / Wave B):** `fix(leonardo): clear PORTD/PORTC/PORTE...` at `437339b` flipped the RED bar to GREEN; `fix(leonardo): add _NOP settling delay...` at `4f205e5` preserved the GREEN bar (regression-guard test stayed PASSED).
- ⬜ **REFACTOR gate:** not applicable — Phase 28 ships the minimum two-commit fix per D-01 atomic-commit-per-RCA-axis. No subsequent refactor commit.

Both commits carry the D-06 footer (RCA + Introducing-commit + Tag presence + Test) — verified via `git log -1 --pretty=%B | grep -E "^(RCA|Introducing-commit|Tag presence|Test):" | wc -l` returning 4 on each commit.

## Self-Check

Verifying claims before finalizing:

| Claim | Check | Status |
|---|---|---|
| Commit 1 SHA captured | `cat /tmp/phase28-wave-b-commit1-sha.txt` = `437339b6879a7493f5f732a46b22b29e7863db24` | verified |
| Commit 2 SHA captured | `cat /tmp/phase28-wave-b-commit2-sha.txt` = `4f205e58ca8f02653bfdda5d65916a8756f54db5` | verified |
| 3 commits ahead of beta | `cd /workspaces/firestarter && git log --oneline beta..HEAD \| wc -l` = 3 | verified |
| Both fix commits' D-06 footer present | `git log -1 --pretty=%B <SHA> \| grep -E "^(RCA\|Introducing-commit\|Tag presence\|Test):" \| wc -l` = 4 on each | verified |
| Exactly 2 `_NOP()` calls in `rurp_read_data_buffer` | `grep -c "_NOP();" src/boards/leonardo_rurp_shield.cpp` = 2 | verified |
| Masked form (NOT `PORTD = 0x00`) | `grep -cF "PORTD = 0x00" src/boards/leonardo_rurp_shield.cpp` = 0 | verified |
| Read-path-only diff | `git diff --name-only bc0f5ac..HEAD -- src/boards/` = single line `src/boards/leonardo_rurp_shield.cpp` | verified |
| Read-path-only hunk count | `git diff bc0f5ac..HEAD -- src/boards/leonardo_rurp_shield.cpp \| grep -c "^@@"` = 2 | verified |
| `pio test -e native` GREEN | exit 0; 22/22 cases pass | verified |
| `pio run -e uno` clean | exit 0; .hex = 62,617 B | verified |
| `pio run -e leonardo` clean | exit 0; .hex = 68,917 B (Δ = +41 B) | verified |
| `pio run -e uno328pb` clean | exit 0; .hex = 62,854 B | verified |
| Leonardo `.hex` Δ within ±200 B | \|68,917 - 68,876\| = 41 ≤ 200 | verified |
| Uno + uno328pb Δ = 0 | both pre = post | verified |
| EVIDENCE.md heading inserted once | `grep -c "^## Phase 28 — Fix Commit References$" .planning/v1.6-EVIDENCE.md` = 1 | verified |
| EVIDENCE.md line-110 anchor preserved | line-110 HTML comment present verbatim | verified |
| EVIDENCE.md line-111 anchor preserved | Phase 29 reserved HTML comment present verbatim (now at line 186) | verified |
| EVIDENCE.md ordering invariant | awk anchor28(110) < heading(112) < anchor29(186) | verified |
| `5b1f1cd` introducing-commit citation in EVIDENCE.md | grep count = 3 (Phase 27 originals + Phase 28 new) | verified |
| `df5fb44` mirror-of citation in EVIDENCE.md | grep count = 5 | verified |
| Per-board sizes table in EVIDENCE.md | 3 rows (uno/leonardo/uno328pb) inside the new section | verified |
| Test file path in EVIDENCE.md | `test/native/avr/test_data_input/test_rurp_set_data_input.cpp` present | verified |
| Branch LOCAL only | `git log origin/v1.6-read-bug` returns "unknown revision" | verified |

## Self-Check: PASSED

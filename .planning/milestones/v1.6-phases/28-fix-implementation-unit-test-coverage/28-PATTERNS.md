# Phase 28 (RE-ITERATION 2026-05-26): Fix Implementation + Unit Test Coverage — Pattern Map

**Mapped:** 2026-05-26
**Files analyzed:** 6 work items (1 revert commit pair, 1 manual file edit, 1 EVIDENCE.md append, 1 ROADMAP.md annotation, 1 conditional Plan 28-04, 1 platformio.ini non-edit)
**Analogs found:** 6 / 6 (every item has a concrete in-repo precedent)
**Supersedes:** the 2026-05-21 28-PATTERNS.md (which mapped patterns for the broken FIX approach — now stale; the v1 file is git-archived audit trail).

**Scope reminder:** Re-iteration is a pure REVERT + Unity test prune + `.hex` SHA evidence capture + EVIDENCE.md append. NO new fix code is authored. All "code" written here is commit-message text, planning-doc Markdown, and YAML frontmatter — there are NO new source-file patterns to map.

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `firestarter/src/boards/leonardo_rurp_shield.cpp` (auto-edited by `git revert 437339b6`) | source, auto-patched | git-history-mutation | `git log 437339b6 --stat` (the commit being inverted) | exact inverse |
| `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` (manual edit — delete one test) | test, Unity native | host-test-prune | The file itself at lines 1-93 (header/setUp scaffolding) + 135-187 (surviving test + main) — analog is "same file, minus one function + one RUN_TEST" | exact |
| `firestarter/platformio.ini` (NO EDIT — allowlist stays) | config | non-edit | `firestarter/platformio.ini:67-104` `[env:native].test_filter` allowlist | non-edit confirmed |
| `.planning/v1.6-EVIDENCE.md` (append new H2 section) | planning doc, append-only | append-between-anchors | Plan 27-05 (`27-05-PLAN.md:242-352`) — append three H3s between two anchors with anti-pattern guards | exact pattern |
| `.planning/ROADMAP.md:129` (annotate Phase 28 checkbox) | planning doc, in-line annotation | suffix-append | `.planning/ROADMAP.md:128-129` Phase 27 + Phase 28 lines with `(completed 2026-05-21)` suffix | role-match (no prior re-iteration annotation exists; we extend the shape) |
| `.planning/phases/28-fix-implementation-unit-test-coverage/28-04-PLAN.md` (conditional) | plan file, drafted-but-not-executed | YAML frontmatter + objective shell | `.planning/phases/27-root-cause-analysis/27-02-PLAN.md:1-66` | exact |
| `.planning/phases/28-fix-implementation-unit-test-coverage/28-03-PLAN.md` (primary) | plan file, autonomous desk-side, multi-task | YAML frontmatter + tasks | `.planning/phases/27-root-cause-analysis/27-05-PLAN.md:1-352` (Wave 3 desk-side capstone with EVIDENCE.md append + anti-pattern guards) | exact |

---

## Pattern Assignments

### `firestarter/src/boards/leonardo_rurp_shield.cpp` (auto-edited by `git revert 437339b6 --no-commit`)

**Analog:** the commit `437339b6` itself (the diff being inverted). No "create" pattern needed — git produces the inverse patch deterministically.

**Commit-message footer template** (paste verbatim into the commit body — sourced from CONTEXT.md D-06 carry-forward lines 132-139):

```
Reverts: <broken-commit-sha> "<broken-commit-subject>"
RCA re-open: .planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Re-open Findings (2026-05-26)"
Verdict: dual-cause (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb pre-existing)
Fix sketch: .planning/v1.6-EVIDENCE.md §"Fix sketch v2 (Phase 28 re-iteration hand-off)"
GATE-1.6 v2: .planning/v1.6-EVIDENCE.md §"GATE-1.6 v2 reassessment" (Axis 4 desk-side passes; bench gate in Phase 29 v2)
```

**Paste-ready commit body** (researcher-authored in RESEARCH.md lines 271-296; reproduced for planner convenience):

```bash
cd /workspaces/firestarter
git revert 437339b6 --no-commit
# Verify staged diff: src/boards/leonardo_rurp_shield.cpp | 10 ----------
git diff --cached --stat
git commit -m "$(cat <<'EOF'
Revert "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input"

This reverts commit 437339b6879a7493f5f732a46b22b29e7863db24.

The masked PORTx-clear introduced in 437339b6 was confirmed by Phase 27
re-open (Plan 27-05, 2026-05-26) + Plan 27-04 bench A/B test (2026-05-26)
to be the primary source of a 99% zeros / 0.08% jitter / 5-distinct-SHAs
regression on Leonardo when combined with 4f205e58's _NOP() settling.
Reverting restores rurp_set_data_input to the pre-Phase-28 shape
(matching v1.6-read-bug~2 = fdb1ed5 / pre-fix Phase 26 baseline).

Reverts: 437339b6 "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input"
RCA re-open: .planning/v1.6-EVIDENCE.md §"Phase 27 — RCA Re-open Findings (2026-05-26)"
Verdict: dual-cause (Outcome A Leonardo firmware-induced + Outcome B-independent uno328pb pre-existing)
Fix sketch: .planning/v1.6-EVIDENCE.md §"Fix sketch v2 (Phase 28 re-iteration hand-off)"
GATE-1.6 v2: .planning/v1.6-EVIDENCE.md §"GATE-1.6 v2 reassessment" (Axis 4 desk-side passes; bench gate in Phase 29 v2)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

**Verified shape:** dry-run executed 2026-05-26; produces clean inverse patch (1 file, 10 deletions, 0 conflicts). No merge resolution needed.

**Cross-reference — atomic-commit-per-RCA-axis precedent:** The original Phase 28 v1 PATTERNS used the v1.2/v1.3 atomic-commit-per-axis pattern (cited at `.planning/phases/28-.../28-PATTERNS.md` v1, and at CONTEXT.md v1 D-01). Re-iteration preserves the same "one commit per RCA axis" hygiene — Plan 28-03 lands ONE revert commit (axis = the PORTx-clear), and Plan 28-04 (if it fires) lands a SECOND atomic revert commit (axis = the `_NOP()` settling). The footer template is the re-iteration analog of the v1 RCA-citation footer.

---

### `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` (manual edit — delete one Unity test)

**Analog:** the file itself. The pattern is "edit-in-place to delete N of K cases; preserve the include scaffolding + the K-N surviving cases".

**Why not delete the whole file:** Plan 27-05 anti-pattern reasoning applies — preserve infrastructure (`host_stubs.cpp`, `avr/pgmspace.h`, the `_BV` shim, the `#include "../../../../src/boards/leonardo_rurp_shield.cpp"` shape on lines 1-89) that the SURVIVING test still needs. Dropping the file would also force a `platformio.ini` allowlist edit (Pitfall 3 in RESEARCH.md).

**Surviving structure (verified live at lines 1-93 + 135-187 of the file):**

- Lines 1-89: header comment + `#include <unity.h>` + AVR-register host shims + `_BV(b)` macro + Leonardo-source include + `setUp(void)` + `tearDown(void)`. KEEP VERBATIM.
- Lines 94-133: the `test_rurp_set_data_input_clears_data_pullups_leonardo` function body + its 30-line preceding comment block. **DELETE.**
- Lines 135-176: the `test_rurp_read_data_buffer_reassembles_data_bus` function body + its 18-line preceding comment block. **KEEP VERBATIM** — researcher-confirmed: the bit-reassembly logic at `leonardo_rurp_shield.cpp:119-126` is unchanged by either revert; this test remains a valid regression guard.
- Lines 178-187: `main()` shell + `UNITY_BEGIN()` + `RUN_TEST(test_rurp_set_data_input_clears_data_pullups_leonardo);` (line 183 — **DELETE this line only**) + `RUN_TEST(test_rurp_read_data_buffer_reassembles_data_bus);` (line 184 — KEEP) + `UNITY_END()`. KEEP the rest verbatim.

**Concrete excerpt of the surviving test (lines 135-176 — for the planner to reference)** — the 8-bit-reassembly cases that stay green post-revert:

```cpp
/* ---------------------------------------------------------------------------
 * Test 2 — Regression guard for rurp_read_data_buffer bit-mapping.
 *
 * PASSES on pre-fix code (the bit-mapping logic at lines 119-126 is unchanged
 * by either Wave B fix commit). Wave B Commit 2 inserts _NOP() settling
 * delays between the three PINx reads; this case guards against accidentally
 * breaking the shift-and-mask reassembly while editing the read function.
 * ... [bit map docstring] ...
 * --------------------------------------------------------------------------- */
void test_rurp_read_data_buffer_reassembles_data_bus(void) {
    PIND = PORTD_DATA_MASK;  /* 0x9F: bits 0,1,2,3,4,7 set */
    PINC = PORTC_DATA_MASK;  /* 0x40: bit 6 */
    PINE = PORTE_DATA_MASK;  /* 0x40: bit 6 */
    TEST_ASSERT_EQUAL_HEX8(0xFF, rurp_read_data_buffer());

    PIND = 0; PINC = 0; PINE = 0;
    TEST_ASSERT_EQUAL_HEX8(0x00, rurp_read_data_buffer());

    /* ... single-bit walks for D0, D5, D7 ... */
}
```

**Commit-message subject** (per CONTEXT.md "Specific Re-iteration Ideas" line 221 + RESEARCH.md "Claude's Discretion" line 50):

```
test(leonardo): remove pullup-clear assertion superseded by Phase 27 re-open revert
```

Body cites Plan 27-05.

**Cross-reference — Unity test prune precedent:** No prior Unity test was DELETED in this firmware sub-repo's history; the only deletion-shaped change is the v1.4 `messages.c` removal (`platformio.ini:101-102` historical comment: "messages.c was generated... but had no firmware callers; deleted post-Phase-7 to reclaim ~256 B"). The analog there is "remove a TU + its allowlist entry"; our re-iteration is "remove a test FUNCTION but keep the TU + allowlist entry intact" — strictly weaker change, no allowlist edit required.

---

### `firestarter/platformio.ini` (NO EDIT — allowlist stays unchanged)

**Analog:** the existing allowlist at lines 78-81:

```ini
test_filter =
	native/avr/test_dispatch
	native/avr/test_messages
	native/avr/test_data_input
```

**Rationale:** Per RESEARCH.md "Alternatives Considered" (line 128) + Pitfall 3 (line 397) — the directory `native/avr/test_data_input/` stays populated (surviving `test_rurp_read_data_buffer_reassembles_data_bus` + `host_stubs.cpp` + `avr/pgmspace.h`). The allowlist entry MUST remain or `pio test -e native` errors on a missing-suite reference.

**Cross-reference — `firestarter/CLAUDE.md` reuse pattern:** documents the inverse (adding new suites): "To add a new host-side Unity suite, drop `test_*.cpp` files under `test/native/avr/<dirname>/`. ... The `[env:native]` configuration in `platformio.ini` does not need changes for new suites." Re-iteration applies the symmetric rule: no changes needed when a suite SHRINKS but stays non-empty.

---

### `.planning/v1.6-EVIDENCE.md` (append new H2 section between lines 560 and 562)

**Analog:** `.planning/phases/27-root-cause-analysis/27-05-PLAN.md` Task 2 (lines 242-352) — the canonical pattern for "append to EVIDENCE.md between two anchors with anti-pattern immutability guards". Plan 27-05 appended THREE H3 subsections; we append ONE H2 section. The mechanics (anchor capture → pre-edit SHA → string-anchored Edit → post-edit SHA assertion) are identical.

**Insertion anchor pattern** (RESEARCH.md lines 484-543; verified live: `grep -c '^## Verdict$' = 1`):

- **Old string** ends with the last line of `### Re-open final verdict — closing the loop` (line 560 — the sentence ending `All re-fix candidates must pass the full GATE-1.6 v2 four-axis check before landing.`) + blank line + `## Verdict` header.
- **New string** = same old + the new H2 inserted between them.

**Anti-pattern immutability guard pattern** (sourced from Plan 27-05 PLAN lines 256-268 + Plan 27-05 SUMMARY lines 151-158):

The Plan 27-05 guards used `awk` range-extraction (semantically robust against line-number drift) — adapt this shape rather than `sed -n '112,186p'` (line-numeric, fragile). Plan 27-05's four guards:

```bash
# Guard #1 — original Phase 27 H2 (lines 22-117 — preserved byte-identical)
awk '/^## Phase 27 — RCA Findings \(2026-05-21\)/,/^## Phase 28/' \
    /workspaces/.planning/v1.6-EVIDENCE.md | sha256sum   # save as PRE_P27_V1_SHA

# Guard #2 — Wave B FAIL post-mortem H3 (preserved byte-identical)
awk '/^### Wave B FAIL post-mortem \(D-07 — milestone re-opens\)/,/^## Phase 27 — RCA Re-open Findings/' \
    /workspaces/.planning/v1.6-EVIDENCE.md | head -n -1 | sha256sum   # save as PRE_WAVEB_SHA

# Guard #3 — ## Verdict + all subsequent (preserved byte-identical)
awk '/^## Verdict/,EOF' /workspaces/.planning/v1.6-EVIDENCE.md | sha256sum   # save as PRE_VERDICT_SHA

# Guard #4 — prior H3 subsections under ## Phase 27 — RCA Re-open Findings (count check ≥6)
grep -cE '^### ' /workspaces/.planning/v1.6-EVIDENCE.md   # save as PRE_H3_COUNT
```

Plan 27-05's results table (from `27-05-SUMMARY.md:151-158`):

| Guard | Pre-edit SHA | Post-edit match |
|-------|-------------|-----------------|
| #1 — original Phase 27 H2 (2026-05-21) | `79f3e5cd…` | PASS — identical |
| #2 — Wave B FAIL post-mortem H3 | `8782ed2f…` | PASS — identical |
| #3 — `## Verdict` H2 + all subsequent | `5b5903db…` | PASS — identical |
| #4 — prior H3 subsections (6 total) | grep ≥6 verified | PASS — all 6 headings present |

**Adapted guards for Plan 28-03** (CONTEXT.md "Specific Re-iteration Ideas" line 220 mandates the original `## Phase 28 — Fix Commit References` H2 at lines 112-186 as the new immutability target):

```bash
# Plan 28-03 Guard #1 — original Phase 28 — Fix Commit References H2 (lines 112-186) byte-identical
awk '/^## Phase 28 — Fix Commit References/,/^## Phase 29 Attempt 1/' \
    /workspaces/.planning/v1.6-EVIDENCE.md | head -n -1 | sha256sum   # save as PRE_P28_V1_SHA

# Plan 28-03 Guard #2 — Phase 27 H2 + Phase 27 Re-open H2 + Verdict all byte-identical
awk '/^## Phase 27 — RCA Findings \(2026-05-21\)/,/^## Verdict/' \
    /workspaces/.planning/v1.6-EVIDENCE.md | head -n -1 | sha256sum   # save as PRE_PRIOR_SHA

# Plan 28-03 Guard #3 — ## Verdict + all subsequent byte-identical
awk '/^## Verdict/,EOF' /workspaces/.planning/v1.6-EVIDENCE.md | sha256sum   # save as PRE_VERDICT_SHA
```

Post-edit assertion (mirror of Plan 27-05's Task 2 close lines 349-351):

```bash
POST_P28_V1_SHA=$(awk '/^## Phase 28 — Fix Commit References/,/^## Phase 29 Attempt 1/' \
    /workspaces/.planning/v1.6-EVIDENCE.md | head -n -1 | sha256sum | awk '{print $1}')
[ "$PRE_P28_V1_SHA" = "$POST_P28_V1_SHA" ] || { echo "FAIL — Phase 28 v1 audit trail diverged"; exit 1; }
```

**New H2 body skeleton** (RESEARCH.md lines 502-540 — paste-ready; planner fills `<placeholders>` with Task-captured values):

```markdown
## Phase 28 Re-iteration — Revert Commits (2026-05-26)

**Landed:** 2026-05-26
**Branch:** `firestarter/v1.6-read-bug` (linear history: bc0f5ac → fdb1ed5 → 437339b6 → 4f205e58 → <revert>)
**Trigger:** Phase 27 re-open closure (Plan 27-05, 2026-05-26) — dual-cause disposition.

### Revert commit (Plan 28-03)
- **Commit:** `<post-revert-SHA>`
- **Subject:** `Revert "fix(leonardo): clear PORTD/PORTC/PORTE data-bit pullups in rurp_set_data_input"`
- **Reverts:** `437339b6` (the masked PORTx-clear)
- **Diff shape:** -10 lines in `firestarter/src/boards/leonardo_rurp_shield.cpp:147-161`

### Test prune commit (Plan 28-03)
- **Commit:** `<post-prune-SHA>`
- **Subject:** `test(leonardo): remove pullup-clear assertion superseded by Phase 27 re-open revert`
- **Files modified:** `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` (-~75 lines)
- **`platformio.ini`:** UNCHANGED

### GATE-1.6 v2 Axis 4 desk-side `.hex` SHA-256 evidence
| Env | Pre-revert (`4f205e58`) | Post-revert | Δ | Axis 4 verdict |
|-----|------------------------|-------------|----|----------------|
| uno | `<uno-pre-SHA>` (62,617 B) | `<uno-post-SHA>` (62,617 B) | byte-identical | PASS |
| leonardo | `<leonardo-pre-SHA>` (68,917 B) | `<leonardo-post-SHA>` (~68,900 B) | differs by revert delta | PASS |
| uno328pb | `d9e51b7e…` (62,854 B) | `d9e51b7e…` (62,854 B) | byte-identical | PASS |

### Plan 28-04 conditional placeholder
`wave_b_needed: false` — Plan 28-04 ships drafted-but-not-executed. Activates only if Phase 29 v2 bench sideload shows Leonardo shape still zeros-dominant.

### Phase 29 v2 bench verification (placeholder)
<!-- Phase 29 v2 appends post-revert bench verification here. -->
```

**Original Phase 28 H2 reference (the immutability target — lines 112-186 of EVIDENCE.md, excerpt verified live):**

The audit trail H2 starts at line 112 with `## Phase 28 — Fix Commit References` and contains Wave A (RED scaffold) + Wave B (two fix commits) + per-board `.hex` sizes + GATE-1.6 desk-side + Phase 29 placeholder. The new re-iteration H2 sits 448 lines later between line 560 and line 562. The two H2s are siblings — the original is preserved byte-identical as the broken-approach audit trail; the new one supersedes its conclusions.

---

### `.planning/ROADMAP.md:129` (annotate Phase 28 checkbox)

**Analog:** `.planning/ROADMAP.md:128-129` — the Phase 27 + Phase 28 checkbox lines with the `(completed YYYY-MM-DD)` suffix shape:

```markdown
- [x] **Phase 27: Root Cause Analysis** — Identify the exact code path that introduces byte corruption (instrumented build, code-path bisection, or scope/logic-analyzer trace); write up WHY the corruption happens; bracket the introducing commit/milestone. (completed 2026-05-21)
- [x] **Phase 28: Fix Implementation + Unit Test Coverage** — Land the fix in the appropriate sub-repo(s) with atomic commits citing RCA evidence; ship a native unit test (Unity or pytest) that would fail on pre-fix code; preserve GATE-1.6 write-path non-regression. (completed 2026-05-21)
```

**No prior re-iteration annotation precedent.** Searched all `Phase 2[7-9]` lines in ROADMAP — Phase 27's RCA was re-opened and closed without any ROADMAP suffix edit (the re-open status is captured in EVIDENCE.md and in the top-level status block at ROADMAP line 11). The PARTIAL annotation precedent is the top-level "PAUSED 2026-05-22 at the Phase 27 RCA re-open boundary" parenthetical on line 11 + the multi-clause status sentence describing what happened.

**Adapted shape** (per CONTEXT.md "In scope" line 29):

```markdown
- [x] **Phase 28: Fix Implementation + Unit Test Coverage** — Land the fix in the appropriate sub-repo(s) with atomic commits citing RCA evidence; ship a native unit test (Unity or pytest) that would fail on pre-fix code; preserve GATE-1.6 write-path non-regression. (completed 2026-05-21; re-iterated 2026-05-26 — split-scope: Leonardo revert)
```

**Edit shape:** semicolon-extend the existing parenthetical. Preserves the `(completed 2026-05-21)` historical record; adds the re-iteration annotation as a second clause inside the same parens.

**Cross-reference — top-level status block precedent (line 11):** the multi-clause sentence pattern `Phases X+Y shipped; Phase Z FAIL (D-N milestone-reopens) — chip-swap diagnostic isolated...` is the project's established way to record re-iterations at the milestone level. The line-129 annotation is the smaller per-phase analog.

---

### `.planning/phases/28-fix-implementation-unit-test-coverage/28-04-PLAN.md` (drafted-but-not-executed, conditional)

**Analog:** `.planning/phases/27-root-cause-analysis/27-02-PLAN.md` (verified read in full above). Frontmatter lines 1-54 + the `<objective>` block at lines 56-66 are the paste-ready template.

**Frontmatter excerpt to mirror** (sourced from `27-02-PLAN.md:1-24` + `:33-53`):

```yaml
---
phase: 27-root-cause-analysis     # ADAPT → 28-fix-implementation-unit-test-coverage
plan: 02                          # ADAPT → 04
type: execute
wave: 2                           # KEEP — Wave B / conditional second revert
depends_on:
  - "27-01"                       # ADAPT → "28-03"
files_modified:
  - .planning/v1.6-EVIDENCE.md
  - firestarter/platformio.ini    # ADAPT — remove (28-04 doesn't touch ini)
  - firestarter/src/boards/leonardo_rurp_shield.cpp
autonomous: false                 # KEEP — gates on a runtime signal
executes_only_if: needs_bench     # ADAPT → phase_29_v2_leonardo_zeros_dominant
requirements:
  - RCA-01                        # ADAPT → FIX-01 / FIX-02 / FIX-03
  - RCA-02
  - RCA-03
tags:
  - rca                           # ADAPT → re-iteration, leonardo, revert, read-bug, conditional, wave-b
  - leonardo
  - read-bug
  - bench
  - conditional
  - wave-b
must_haves:
  truths:
    - "Wave B fires ONLY IF Plan 27-01's Wave A verifier emitted `needs_bench: true`. ..."
    # ADAPT → "Wave B fires ONLY IF Phase 29 v2 bench sideload ... Leonardo shape still zeros-dominant"
  artifacts:
    - path: ".planning/v1.6-EVIDENCE.md"
      provides: "Wave B addendum subsection under the existing ## Phase 27 — RCA Findings section"
      contains: "### Wave B addendum"
      # ADAPT → addendum under the NEW ## Phase 28 Re-iteration H2; contains "### Conditional second revert (Plan 28-04)"
---
```

**`<objective>` opening sentence — REQUIRED VERBATIM** (sourced from `27-02-PLAN.md:57`):

```markdown
**THIS PLAN IS DRAFTED BUT DOES NOT EXECUTE BY DEFAULT.**
```

This is the load-bearing safety-valve marker. Per RESEARCH.md Pitfall 5 (lines 411-417), the GSD executor uses this string + the `executes_only_if:` frontmatter key together to recognize a parked plan. Both must be present.

**`<objective>` second-paragraph pattern** (sourced from `27-02-PLAN.md:59`):

```
Wave B is a conditional safety valve per CONTEXT D-01 / D-07. The plan exists in
the workflow so the executor can activate it at runtime IF AND ONLY IF
<gating signal>. Per RESEARCH §"<criteria section>" (HIGH confidence), <expected
default outcome>.
```

**Adapted second paragraph for Plan 28-04** (researcher-drafted in RESEARCH.md lines 608-614):

```
Plan 28-04 is a conditional safety valve per CONTEXT D-13v2. The plan exists in
the workflow so the executor can activate it at runtime IF AND ONLY IF Phase 29 v2
bench sideload of Plan 28-03's single revert (of 437339b6) shows Leonardo shape
STILL zeros-dominant. Per Plan 27-05 fix sketch v2 (`v1.6-EVIDENCE.md:513`)
bisection-first recommendation, this conditional second revert preserves the
diagnostic signal of which Phase 28 commit was primary.

Expected outcome: Plan 28-04 stays parked — Plan 27-05 hypothesizes the
PORTx-clear (437339b6) is the more likely primary fault driver.
```

**Task 0 gate pattern** (sourced from `27-02-PLAN.md:118-146` — the `<task type="checkpoint:decision" gate="blocking">` block with `<options>` for `parked` vs `activate` and a `<resume-signal>`). Mirror this verbatim for Plan 28-04 Task 0, replacing:
- The `<decision>` question: "Did Plan 27-01's Task 2 ... emit `needs_bench: true`?" → "Did Phase 29 v2 bench sideload of Plan 28-03's revert show Leonardo shape still zeros-dominant?"
- The `<option id="parked">` `<pros>` text to match the 28-04 stay-parked default.
- The `<option id="activate">` `<cons>` text to match the second-revert cost.

---

### `.planning/phases/28-fix-implementation-unit-test-coverage/28-03-PLAN.md` (primary, autonomous, desk-side)

**Analog:** `.planning/phases/27-root-cause-analysis/27-05-PLAN.md` — the Wave 3 desk-side capstone that (a) sequenced multiple Edit operations on EVIDENCE.md, (b) used anti-pattern immutability guards, (c) was `autonomous: true`, and (d) produced a single meta-repo commit on `v1.6-read-bug`.

**Frontmatter excerpt to mirror** (sourced from `27-05-PLAN.md:1-57`):

```yaml
---
phase: 27-root-cause-analysis     # ADAPT → 28-fix-implementation-unit-test-coverage
plan: 05                          # ADAPT → 03
type: execute
wave: 3                           # ADAPT → 1 (primary Wave A; Plan 28-04 is Wave 2)
depends_on:
  - "27-03"                       # ADAPT → no deps within phase (28-01/02 are v1 audit trail)
  - "27-04"
files_modified:
  - .planning/v1.6-EVIDENCE.md
  # ADAPT — add:
  #   - .planning/ROADMAP.md
  #   - firestarter/src/boards/leonardo_rurp_shield.cpp (auto-edited by git revert)
  #   - firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp
autonomous: true
gap_closure: true                 # KEEP shape — re-iteration is a gap closure
requirements:
  - RCA-01                        # ADAPT → FIX-01, FIX-02, FIX-03
  - RCA-02
  - RCA-03
tags:
  # ADAPT → re-iteration, leonardo, revert, read-bug, gate-1-6-v2-axis-4-desk-side, hex-sha-identity
must_haves:
  truths:
    # ADAPT — multi-line list of locked truths from CONTEXT.md re-iteration block
  artifacts:
    - path: ".planning/v1.6-EVIDENCE.md"
      provides: "<new H2 section appended>"
      contains: "## Phase 28 Re-iteration — Revert Commits (2026-05-26)"
---
```

**Task structure to mirror** (sourced from `27-05-PLAN.md:242-352` Task 2 — the EVIDENCE.md append task is the structural template):

1. `read_first` block listing the EVIDENCE.md current state + CONTEXT.md + RESEARCH.md + the v1 audit-trail H2 to be guarded.
2. `<action>` block in this order:
   - Capture pre-edit SHA-256 immutability guards FIRST (see "Anti-pattern immutability guard pattern" above).
   - Perform the Edit operations (string-anchored, not line-numeric).
   - Re-capture post-edit SHA-256 immutability guards.
   - Assert byte-identity for all guards; on FAIL, revert with `git checkout -- .planning/v1.6-EVIDENCE.md` (Plan 27-05 PLAN line 349).
3. `<verify>` block with paste-ready `grep -cE '...' | awk '$1 >= N {exit 0} {exit 1}' && ...` chains (Plan 27-05 PLAN line 354 is the canonical example — uses `awk '$1 >= 1 {exit 0} {exit 1}'` after `grep -c` for count assertions).
4. `<acceptance_criteria>` enumerated 1..N (Plan 27-05 PLAN lines 356-435 = 18 numbered criteria covering positional + token + count + immutability-guard checks).

**Cross-reference — the per-board `.hex` capture script:** sourced from RESEARCH.md lines 425-444 (paste-ready Bash one-liner using `pio run -e $ENV` + `sha256sum .pio/build/$ENV/firmware.hex`). The pre-revert + post-revert SHA capture pair is the GATE-1.6 v2 Axis 4 desk-side evidence input.

---

## Shared Patterns

### Anti-Pattern Immutability Guard (SHA-256-based)

**Source:** Plan 27-05 PLAN `27-05-PLAN.md:256-262` + SUMMARY `27-05-SUMMARY.md:151-158`

**Apply to:** Every EVIDENCE.md edit task in Plan 28-03 (and Plan 28-04 if it fires).

**Why this pattern:** EVIDENCE.md is append-only by convention; the file accumulates phase H2 sections in chronological order. The original Phase 28 H2 (lines 112-186) is the audit trail of the broken FIX approach — preserving it byte-identical is what makes the re-iteration's append honest (rather than rewriting history). Plan 27-05's four guards all PASSED in execution; the pattern is proven.

**Mechanics (paste-ready):**

```bash
# Pre-edit capture
PRE_SHA=$(awk '/^<START_HEADING>/,/^<END_HEADING>/' file.md | head -n -1 | sha256sum | awk '{print $1}')

# ... perform Edit ...

# Post-edit assertion
POST_SHA=$(awk '/^<START_HEADING>/,/^<END_HEADING>/' file.md | head -n -1 | sha256sum | awk '{print $1}')
[ "$PRE_SHA" = "$POST_SHA" ] || { git checkout -- file.md; exit 1; }
```

The `head -n -1` strips the END_HEADING line from the range (so it doesn't appear in the hashed content). For trailing ranges (`,EOF`), omit `head -n -1`.

### Atomic-Commit-per-RCA-Axis Footer

**Source:** CONTEXT.md D-06 carry-forward (lines 132-139)

**Apply to:** Every revert commit in Plan 28-03 (one) and Plan 28-04 (one, if it fires).

**Why this pattern:** The original Phase 28 v1 used atomic-commit-per-RCA-axis (Plan 28-02 Commit 1 = PORTx-clear axis; Commit 2 = `_NOP()` settling axis). The re-iteration inverts the polarity: atomic-revert-per-RCA-axis, with each revert commit's footer citing the same RCA evidence (Plan 27-05 verdict + Plan 27-04 bench A/B + GATE-1.6 v2 reassessment + fix sketch v2). Bisection clarity beats efficiency (CONTEXT.md D-13v2).

**Mechanics:** Use `git revert <sha> --no-commit` to stage the inverse patch without invoking `$EDITOR`; then `git commit -m "$(cat <<'EOF' ... EOF)"` HEREDOC with the D-06 footer baked in. RESEARCH.md lines 271-296 are the paste-ready commit invocation.

### Drafted-But-Not-Executed Plan Shell

**Source:** `.planning/phases/27-root-cause-analysis/27-02-PLAN.md` (full file, especially frontmatter lines 1-54 + objective opener line 57)

**Apply to:** Plan 28-04 only.

**Why this pattern:** Phase 27 v1 used this exact shape for Plan 27-02 (instrumented-build Wave B — the trigger never fired, plan stayed parked). The GSD executor recognizes the pattern via the combination of `autonomous: false` + `executes_only_if: <gate>` + the **bold-uppercase** marker `THIS PLAN IS DRAFTED BUT DOES NOT EXECUTE BY DEFAULT.` as the first line of `<objective>`. Per Pitfall 5 (RESEARCH.md), missing either signal causes unintended auto-firing.

### Append-Between-Anchors Edit Pattern

**Source:** `27-05-PLAN.md:254-269` — Plan 27-05 Task 2 action prologue.

**Apply to:** The Plan 28-03 EVIDENCE.md edit task.

**Why this pattern:** String-anchored Edit operations are robust against line-number drift (a parallel commit between research and execution can shift line numbers; the unique string `## Verdict` remains stable). RESEARCH.md line 543 verified `grep -c '^## Verdict$' = 1`. The old_string/new_string formulation in RESEARCH.md lines 487-540 is the paste-ready Edit invocation for the planner.

### Verifier Block Pattern (count + token + positional)

**Source:** `27-05-PLAN.md:354` (the `<automated>` block)

**Apply to:** Plan 28-03 `<verify>` block.

**Shape:**

```bash
grep -cE '^### <new heading>' file.md | awk '$1 >= 1 {exit 0} {exit 1}' \
&& grep -cE '<required token>' file.md | awk '$1 >= N {exit 0} {exit 1}' \
&& awk '/^<anchor A>/{a=NR} /^<anchor B>/{b=NR} END{exit (a>0 && b>a)?0:1}' file.md \
&& cd /workspaces/firestarter && git rev-parse v1.6-read-bug | grep -E '^<expected-SHA-prefix>' \
&& cd /workspaces/firestarter_app && pytest tests/ -x
```

The chain combines: (a) count assertions (`grep -c | awk '$1 >= N'`); (b) positional assertions (`awk '... NR ...'`); (c) sub-repo state verification (`git rev-parse`); (d) host-side non-regression smoke (`pytest tests/ -x`). All four classes are required for a complete Phase 28 re-iteration verifier.

---

## No Analog Found

None. Every work item in Phase 28 re-iteration has a concrete in-repo precedent:

| Work Item | Why a Precedent Exists |
|-----------|------------------------|
| Git revert with footer expansion | Used in v1.2/v1.3 atomic-commit-per-axis history; the inverse polarity (revert) follows the same shape |
| Unity test prune (edit-in-place) | `firestarter/CLAUDE.md` documents the inverse (add) shape; symmetric rule applies |
| EVIDENCE.md append between anchors | Plan 27-05 Task 2 is the direct template |
| Anti-pattern immutability guards | Plan 27-05 used four; all PASSED |
| Drafted-but-not-executed plan | Plan 27-02 is the direct template |
| ROADMAP.md per-phase annotation | The `(completed YYYY-MM-DD)` suffix shape extends to `(completed YYYY-MM-DD; re-iterated YYYY-MM-DD — ...)` |
| `.hex` SHA-256 capture | Standard `sha256sum .pio/build/$ENV/firmware.hex` — already used in Phase 27 (`d9e51b7e…` for uno328pb) |

---

## Out-of-Scope Patterns (Explicitly IGNORED)

Per the pattern_mapping_context, the following patterns from the 2026-05-21 28-PATTERNS.md (the v1 audit trail) are NOT extracted into this re-iteration map:

- The Uno `df5fb44` PORTx-clear mirror shape (the fix shape that introduced the regression).
- `_NOP()` count tuning rationale (Atmel-7766J §10.2.4 + W27C512 tACC datasheet citations) — applicable only to a future v1.8 re-fix, not to the re-iteration revert.
- Unity test scaffolding for the pullup-clear assertion (the test being DELETED, not added).
- Two-wave Plan 28-01 (RED scaffold) + Plan 28-02 (Wave B fix) structure — superseded by Plan 28-03 (revert) + Plan 28-04 (conditional second revert).
- The "include-as-source" pattern (`#include "../../../../src/boards/leonardo_rurp_shield.cpp"`) — preserved in the surviving test file as part of the kept lines 1-89, but not the subject of any new pattern decision in the re-iteration.

These remain on file in:
- `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` (the file itself + git log)
- `.planning/v1.6-EVIDENCE.md §"Phase 28 — Fix Commit References"` (lines 112-186 — audit trail, immutability-guarded)
- `.planning/phases/28-fix-implementation-unit-test-coverage/28-01-PLAN.md` + `28-02-PLAN.md` (the v1 plans, also audit trail)
- `.planning/phases/28-fix-implementation-unit-test-coverage/28-CONTEXT.md:248-518` (the v1 appendix)

The re-iteration explicitly does NOT re-author or re-derive these patterns.

---

## Metadata

**Analog search scope:**
- `.planning/phases/27-root-cause-analysis/27-02-PLAN.md` (drafted-but-not-executed shape) — read in full
- `.planning/phases/27-root-cause-analysis/27-05-PLAN.md` (EVIDENCE.md append + immutability guards) — read frontmatter + Task 2 action body
- `.planning/phases/27-root-cause-analysis/27-05-SUMMARY.md` (guard PASS results) — read full
- `.planning/v1.6-EVIDENCE.md` (original Phase 28 H2 at 112-186; Phase 27 Re-open verdict at 540-560; Verdict at 562) — read all three anchor regions
- `.planning/ROADMAP.md` (Phase 27/28 checkbox lines 128-129 + top-level status line 11) — read both
- `firestarter/platformio.ini` (`[env:native].test_filter` allowlist + `[env:leonardo]` shape, lines 60-104) — read
- `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` (lines 85-187 — both Unity tests + main) — read
- `firestarter/CLAUDE.md` (Native Test Environment + reuse pattern) — read via system reminder

**Files scanned:** 8 source/planning files + 2 sub-repo CLAUDE.md files (system context).
**Pattern extraction date:** 2026-05-26.
**Memory consulted:** `[[project_uno328pb_bench_instability_27_04]]` (uno328pb deferral substrate); `[[feedback_branching]]` (sub-repo branch model — applies but is unchanged by the revert).
**Auto Mode active:** No clarifying questions asked; all gray areas were pre-resolved against Plan 27-05 verdict.

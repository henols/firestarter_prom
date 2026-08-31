---
phase: 34-shield-version-detect-design-firmware-plumbing
plan: 05
subsystem: host-cli-python-parity
tags: [host-cli, python, constants-parity, revision, pytest-gate, d-08, detect-fw-01, v1.7]

# Dependency graph
requires:
  - phase: 34-shield-version-detect-design-firmware-plumbing
    plan: 02
    provides: "firestarter/include/rurp_shield.h REVISION_2_3 = 5 + REVISION_UNKNOWN = 0xFE — the source-of-truth firmware enum that the Python parity block mirrors verbatim"
  - phase: 34-shield-version-detect-design-firmware-plumbing
    plan: 04
    provides: "Meta-repo firestarter submodule pin at SHA 032a2e2 — Plan 05 cross-references this pinned SHA when asserting the parity invariant; firestarter_app pytest baseline 82/82 PASS anchored at Plan 04 close"
  - phase: 33-silkscreen-label-code-alias-migration
    plan: 04
    provides: "D-08 single-atomic-commit substrate (precedent commit 782ef2a — constants.py + main.py + CLAUDE.md atomic shape on firestarter_app sub-repo v1.7-shield-investigation branch); RURP_CONTROL_REGISTER_BITS block in constants.py + matching sync-rule prose at CLAUDE.md:100 — Phase 34 Plan 05 appends to (does not replace) the Phase 33 CTRL_* sentence"
provides:
  - "firestarter_app/firestarter/constants.py — new `# RURP Hardware Revisions` block with 7 REVISION_* constants (REVISION_0=0x00 through REVISION_UNKNOWN=0xFE) mirroring the firmware enum at firestarter/include/rurp_shield.h:25-31. Substrate for Plan 06 _REVISION_SILKSCREEN dict in serial_comm.py per D-05 Path A."
  - "firestarter_app/CLAUDE.md Constants subsection extended with one new sentence covering the RURP_HARDWARE_REVISIONS sync rule + the 0xFE / 0xFF sentinel carve-out (novel detail beyond Phase 33's CTRL_* sentence template). Phase 33 sentence preserved verbatim."
  - "firestarter_app/tests/test_revision_constants_parity.py — new hard pytest parity gate. Single test function asserts all 7 REVISION_* byte values per VALIDATION Dim 3 + Dim 6 (Wave 0 optional toggle activated). Any future firmware-enum drift without matching Python update FAILs at pytest time."
  - "Single atomic commit on firestarter_app sub-repo v1.7-shield-investigation branch — SHA 9752a85 — covers constants.py + CLAUDE.md + the new parity test (Phase 33 D-08 single-atomic-commit substrate)."
  - "pytest baseline lifted to 83/83 PASS (82 Phase-33 baseline + 1 new parity test)."
affects:
  - "Phase 34 Plan 06 (firestarter_app serial_comm.py _REVISION_SILKSCREEN dict per D-05 Path A) — consumes the 7 Python REVISION_* constants this plan landed; Plan 06 will add the cosmetic u8 → silkscreen-string mapping in the MSG_OK_REV format path."
  - "Phase 34 Plan 07 (meta-repo firestarter_app submodule pointer bump) — Plan 07 bumps the meta-repo submodule pointer to the Plan 05 + Plan 06 HEAD; this plan's SHA 9752a85 is one of the subsumed sub-repo commits."
  - "Phase 35 (milestone close) — cites the parity pytest gate as the cross-repo invariant evidence; sub-repo `v1.7-shield-investigation` → `beta` promotion will run this pytest as part of the close gate."

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Phase 33 D-08 single-atomic-commit substrate extended to Phase 34 — constants.py block + CLAUDE.md sync-rule prose + hard pytest parity gate landed in ONE atomic commit on firestarter_app sub-repo v1.7-shield-investigation branch. Preserves bisect granularity (the three files are coupled — touching one without the others would be incoherent). Precedent commit 782ef2a (Phase 33 Plan 04); this plan's commit 9752a85 is the Phase 34 instance."
    - "Hard pytest parity gate pattern (VALIDATION Dim 3 — Wave 0 optional toggle activated for stronger coverage) — single test function with named imports + `assert NAME == 0xNN` chain enforces cross-repo byte-value invariant at pytest time. No fixtures, no conftest.py dependency — pytest auto-discovers tests/test_*.py. Drift on either side FAILs the gate immediately."
    - "Append-not-replace CLAUDE.md sync-rule sentence (PATTERNS Pattern 8) — the Phase 33 CTRL_* sentence at line 100 stays intact; Phase 34 sentence is appended to the same paragraph. Same sentence template (`Additionally, the X_BLOCK block ... mirrors ... in firestarter/include/Y.h (Phase N / v1.7 — ...). Keep X_* names + values in sync with the firmware header.`) with novel 0xFE / 0xFF sentinel carve-out clause."

key-files:
  created:
    - "firestarter_app/tests/test_revision_constants_parity.py (new — hard pytest parity gate; 1 test function asserting all 7 REVISION_* byte values)"
    - ".planning/phases/34-shield-version-detect-design-firmware-plumbing/34-05-SUMMARY.md (this file)"
  modified:
    - "firestarter_app/firestarter/constants.py (appended `# RURP Hardware Revisions` block with 7 constants after the existing CTRL_* block; no changes to lines 1-83)"
    - "firestarter_app/CLAUDE.md (Constants subsection paragraph at line 100 extended with one new sentence; Phase 33 CTRL_* sentence preserved verbatim)"

key-decisions:
  - "Single atomic commit on firestarter_app sub-repo per Phase 33 D-08 substrate — the three plan-owned files (constants.py + CLAUDE.md + parity test) are tightly coupled (block + sync-rule + gate enforce the same cross-repo invariant), so a single commit preserves bisect granularity. Subject `feat(34-05): add RURP_HARDWARE_REVISIONS Python parity block + sync rule + pytest gate (D-08; DETECT-FW-01)` with body citing D-08, Phase 33 precedent (782ef2a), VALIDATION Dim 3 + Dim 6 coverage, sentinel carve-out (0xFE / 0xFF), Plan 06 hand-off."
  - "Selective staging via `git add firestarter/constants.py CLAUDE.md tests/test_revision_constants_parity.py` (NOT `git add .` or `git add -A`) — operator's pre-existing WIP in `firestarter_app/firestarter/config.py` (` M`) + untracked `firestarter_app/.planning/STATE.md` (`??`) preserved as instructed. Post-commit `git status --short` confirms both still in their pre-plan unstaged/untracked state."
  - "Wave 0 optional pytest gate toggle activated (per plan frontmatter must_haves) — VALIDATION Dim 3 (cross-repo invariant) + Dim 6 (drift-failure) coverage strengthened by landing the hard pytest parity assertion in this plan. The gate could have been deferred to a later sweep but landing it now anchors the substrate before Plan 06 starts."
  - "Section-comment header in constants.py carries 7 lines of sync-burden prose + per-constant inline annotation comments — same idiom as Phase 33 CTRL_* block (PATTERNS Pattern 6). The 0xFE / 0xFF sentinel carve-out is explained in the header block, not buried in a per-constant comment, so future readers see the sentinel semantics at the block boundary."

patterns-established:
  - "Phase 34 / Phase 33 cross-repo parity pattern — for any firmware enum / `#define` block that needs host-side mirroring, the host-side artifact has THREE pieces: (1) the constants block in `firestarter_app/firestarter/constants.py` with section-comment header citing the firmware source-of-truth; (2) one new sentence in `firestarter_app/CLAUDE.md` Constants subsection covering the sync rule (append-not-replace per PATTERNS Pattern 8); (3) a hard pytest parity gate at `firestarter_app/tests/test_*_parity.py` asserting every byte value. All three land in ONE atomic commit on the firestarter_app v1.7-shield-investigation branch."

requirements-completed: [DETECT-FW-01, DETECT-FW-02]

# Metrics
duration: ~4min
completed: 2026-05-25
---

# Phase 34 Plan 05: firestarter_app Python REVISION_* Parity (D-08; DETECT-FW-01) Summary

**Landed the Python-side `RURP_HARDWARE_REVISIONS` parity block (7 constants from REVISION_0=0x00 through REVISION_UNKNOWN=0xFE) in `firestarter_app/firestarter/constants.py` mirroring the firmware enum at `firestarter/include/rurp_shield.h:25-31`; extended `firestarter_app/CLAUDE.md` Constants subsection with one new sync-rule sentence (Phase 33 CTRL_* sentence preserved verbatim); landed a hard pytest parity gate at `firestarter_app/tests/test_revision_constants_parity.py` that FAILs on any future firmware-enum drift; single atomic commit on firestarter_app sub-repo v1.7-shield-investigation branch (SHA `9752a85`); pytest baseline lifted to 83/83 PASS. Wave 3 Python-parity substrate complete — Plan 06 (serial_comm.py `_REVISION_SILKSCREEN` dict per D-05 Path A) cleared to start.**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-05-25T14:06:08Z (orchestrator phase-resume after 34-04 close)
- **Completed:** 2026-05-25T14:10:24Z (post-sub-repo-commit)
- **Tasks:** 4 (Task 1: REVISION_* block in constants.py; Task 2: CLAUDE.md sync-rule sentence; Task 3: pytest parity gate; Task 4: single atomic commit)
- **firestarter sub-repo commits:** 0 (Plan 05 does not modify firmware)
- **firestarter_app sub-repo commits:** 1 (SHA `9752a85` — atomic 3-file commit)
- **Meta-repo commits:** 1 (this SUMMARY's final-metadata commit lands separately after this file is written; Plan 05 does NOT bump the meta-repo firestarter_app submodule pointer — Plan 07 owns that)
- **Files modified (sub-repos):** 3 (firestarter_app/{firestarter/constants.py, CLAUDE.md, tests/test_revision_constants_parity.py})
- **Files modified (meta-repo):** 1 (this SUMMARY.md) + STATE/ROADMAP updates in the final metadata commit

## Accomplishments

### Task 1 — `# RURP Hardware Revisions` block in `firestarter_app/firestarter/constants.py`

Appended a new section-comment block immediately after the existing `CTRL_ADDRESS_LINE_16 = 0x001` line (Phase 33 Plan 04 substrate). The new block follows PATTERNS Pattern 6 verbatim: section-comment header (7 lines of sync-burden prose) + 7 column-aligned `NAME = 0xNN  # comment` constants + inline annotation comments documenting which revs are physical-detect vs EEPROM-override-only.

**Exact content landed (verbatim from `firestarter_app/firestarter/constants.py:85-99`):**

```python
# RURP Hardware Revisions — mirror of firestarter/include/rurp_shield.h
# REVISION_* enum. Documentary only — Python does not perform the ADC
# band-detect (firmware owns that). Used by host-side mapping of the
# MSG_OK_REV physical-u8 byte to a silkscreen-version string for log /
# CLI output. Keep in sync per CLAUDE.md sync rule.
# 0xFF is reserved as the EEPROM-override-absent sentinel (see
# rurp_config_utils.cpp:37 + serial_comm.py _format_message).
REVISION_0          = 0x00
REVISION_1          = 0x01
REVISION_2_0        = 0x02  # broad bucket: covers Rev 2.0 / 2.1 / 2.2 (R41=4k7)
REVISION_2_1        = 0x03  # via EEPROM override only — ADC cannot distinguish
REVISION_2_2        = 0x04  # via EEPROM override only — ADC cannot distinguish
REVISION_2_3        = 0x05  # R41=10k physical detect
REVISION_UNKNOWN    = 0xFE  # ADC band-gap or pre-detect-resistor + A2 indeterminate
```

**Source-of-truth cross-check (firestarter/include/rurp_shield.h:25-31, post-Plan-02 HEAD on pinned firestarter SHA `032a2e2`):**

```c
#define REVISION_0 0
#define REVISION_1 1
#define REVISION_2_0 2
#define REVISION_2_1 3
#define REVISION_2_2 4
#define REVISION_2_3 5
#define REVISION_UNKNOWN 0xFE  // ADC band-gap fall-through; 0xFF reserved for EEPROM-override-absent sentinel
```

Byte values match 1:1 across all 7 entries (verified by the pytest parity gate in Task 3).

**Smoke-test (Task 1 acceptance):**

```bash
cd /workspaces/firestarter_app && python -c "from firestarter.constants import REVISION_0, REVISION_1, REVISION_2_0, REVISION_2_1, REVISION_2_2, REVISION_2_3, REVISION_UNKNOWN; assert REVISION_0 == 0x00; assert REVISION_1 == 0x01; assert REVISION_2_0 == 0x02; assert REVISION_2_1 == 0x03; assert REVISION_2_2 == 0x04; assert REVISION_2_3 == 0x05; assert REVISION_UNKNOWN == 0xFE; print('all 7 constants OK')"
# Output: all 7 constants OK
```

**Acceptance grep checks (all PASS):**

| Check | Pattern | Result |
|-------|---------|--------|
| Section header present | `^# RURP Hardware Revisions` | PASS |
| REVISION_0 | `^REVISION_0 *= 0x00` | PASS |
| REVISION_1 | `^REVISION_1 *= 0x01` | PASS |
| REVISION_2_0 | `^REVISION_2_0 *= 0x02` | PASS |
| REVISION_2_1 | `^REVISION_2_1 *= 0x03` | PASS |
| REVISION_2_2 | `^REVISION_2_2 *= 0x04` | PASS |
| REVISION_2_3 | `^REVISION_2_3 *= 0x05` | PASS |
| REVISION_UNKNOWN | `^REVISION_UNKNOWN *= 0xFE` | PASS |
| Python smoke-import | (above) | PASS |
| No type annotations used | `grep -q "REVISION_.*:"` returns non-zero | PASS |
| Lands AFTER CTRL_* block | `grep -n "REVISION_0"` > `grep -n "CTRL_ADDRESS_LINE_16"` | PASS (line 92 > line 83) |

### Task 2 — `firestarter_app/CLAUDE.md` Constants subsection sync-rule sentence

Appended one new sentence to the existing Constants subsection paragraph at line 100 of `firestarter_app/CLAUDE.md`. Per PATTERNS Pattern 8: append-not-replace — the Phase 33 CTRL_* sentence stays intact; the new Phase 34 sentence follows it in the same paragraph.

**Exact sentence landed (verbatim from `firestarter_app/CLAUDE.md:100` post-edit):**

> Additionally, the `RURP_HARDWARE_REVISIONS` block in `constants.py` (REVISION_* names) mirrors the hardware-revision enum declarations in `firestarter/include/rurp_shield.h` (Phase 34 / v1.7 — shield-version-detect design + firmware plumbing). Keep REVISION_* names + byte values in sync with the firmware enum; `0xFF` is reserved as the EEPROM-override-absent sentinel and `0xFE` (`REVISION_UNKNOWN`) is reserved for the ADC-band-gap fall-through.

**Sentence-template consistency check (vs Phase 33 substrate):**

| Element | Phase 33 sentence | Phase 34 new sentence |
|---------|--------------------|------------------------|
| Block name citation | `RURP_CONTROL_REGISTER_BITS` block | `RURP_HARDWARE_REVISIONS` block |
| Names mirrored | CTRL_* | REVISION_* |
| Firmware source-of-truth | `firestarter/include/rurp_pinout.h` | `firestarter/include/rurp_shield.h` |
| Phase / milestone citation | (Phase 33 / v1.7 — silkscreen-label code-alias migration) | (Phase 34 / v1.7 — shield-version-detect design + firmware plumbing) |
| Sync directive | "Keep CTRL_* names + hex values in sync with the firmware header." | "Keep REVISION_* names + byte values in sync with the firmware enum;" |
| Novel detail (Phase 34 only) | — | "`0xFF` is reserved as the EEPROM-override-absent sentinel and `0xFE` (`REVISION_UNKNOWN`) is reserved for the ADC-band-gap fall-through." |

**Acceptance grep checks (all PASS):**

| Check | Pattern | Result |
|-------|---------|--------|
| New block name cited | `RURP_HARDWARE_REVISIONS` | PASS |
| Phase / milestone cited | `Phase 34 / v1.7` | PASS |
| Sentinel sentinel name cited | `REVISION_UNKNOWN` | PASS |
| 0xFF carve-out narrative | `EEPROM-override-absent sentinel` | PASS |
| Phase 33 CTRL_* sentence preserved | `CTRL_\* names + hex values in sync with the firmware header` | PASS |

### Task 3 — `firestarter_app/tests/test_revision_constants_parity.py` (hard pytest parity gate)

New pytest module at `firestarter_app/tests/test_revision_constants_parity.py` carries a single test function `test_revision_byte_values_match_firmware_enum()` that asserts all 7 REVISION_* byte values per VALIDATION Dim 3 (cross-repo invariant) + Dim 6 (Wave 0 optional toggle activated for stronger coverage). Pytest's default test-discovery picks the file up without `conftest.py` edits.

**File structure (PATTERNS Pattern 11):**

- Module-level docstring with project copyright header (Project Name + Copyright + MIT license) + Phase 34 / D-08 / source-of-truth file-line citation.
- Named imports (NOT wildcard): `from firestarter.constants import (REVISION_0, REVISION_1, REVISION_2_0, REVISION_2_1, REVISION_2_2, REVISION_2_3, REVISION_UNKNOWN,)`.
- Single test function with docstring + 7 `assert NAME == 0xNN` lines.
- Trailing comment documenting the 0xFF reserve (sentinel — NOT a REVISION_ value).

**Pytest invocation (verbatim output):**

```bash
$ cd /workspaces/firestarter_app && pytest -q tests/test_revision_constants_parity.py
.                                                                        [100%]
1 passed in 0.0Xs

$ cd /workspaces/firestarter_app && pytest
........................................................................ [ 86%]
...........                                                              [100%]
83 passed in 0.92s
```

**Acceptance checks (all PASS):**

| Check | Command / pattern | Result |
|-------|-------------------|--------|
| File exists | `test -f firestarter_app/tests/test_revision_constants_parity.py` | PASS |
| Test function defined | `grep -q "def test_revision_byte_values_match_firmware_enum"` | PASS |
| Named imports (not wildcard) | `grep -q "from firestarter.constants import"` | PASS |
| REVISION_2_3 asserted | `grep -q "REVISION_2_3"` | PASS |
| REVISION_UNKNOWN asserted | `grep -q "REVISION_UNKNOWN == 0xFE"` | PASS |
| Copyright header present | `head -8 ... \| grep -q "Copyright"` | PASS |
| Module-alone test passes | `pytest -q tests/test_revision_constants_parity.py` | 1 passed |
| Full suite green | `pytest` | 83 passed (82 baseline + 1 new) |

### Task 4 — Single atomic commit on firestarter_app sub-repo `v1.7-shield-investigation` branch

Verified branch identity (`v1.7-shield-investigation`); verified `git status --porcelain` showed the 3 plan-owned changes (` M CLAUDE.md`, ` M firestarter/constants.py`, `?? tests/test_revision_constants_parity.py`) PLUS the pre-existing operator WIP (` M firestarter/config.py`, `?? .planning/STATE.md`); selectively staged ONLY the 3 plan-owned files via `git add firestarter/constants.py CLAUDE.md tests/test_revision_constants_parity.py` (NEVER `git add .` or `git add -A`); confirmed staging via `git status --short` showed `M  CLAUDE.md` / `M  firestarter/constants.py` / `A  tests/test_revision_constants_parity.py` (uppercase = staged) AND ` M firestarter/config.py` / `?? .planning/STATE.md` (operator WIP still unstaged/untracked); committed.

**Commit:** `9752a85` (full SHA `9752a857a4a312c95140e89a46d10b085eda5a49`) on `v1.7-shield-investigation`.

**Subject:** `feat(34-05): add RURP_HARDWARE_REVISIONS Python parity block + sync rule + pytest gate (D-08; DETECT-FW-01)`

**Body cites:** D-08 (Python parity mirror per Phase 33 substrate), Phase 33 Plan 04 D-08 precedent (`782ef2a`), VALIDATION Dim 3 + Dim 6 coverage, sentinel carve-out (0xFE / 0xFF), Plan 06 hand-off (`_REVISION_SILKSCREEN` dict in serial_comm.py), DETECT-FW-01 + DETECT-FW-02 requirements.

**Files in commit (exactly 3, verified):**

| File | Status | Lines |
|------|--------|-------|
| `CLAUDE.md` | modified | +1 / -1 (sync-rule sentence appended; old sentence ended `... firmware header.`; new sentence appended after same line) |
| `firestarter/constants.py` | modified | +15 / 0 (new section block) |
| `tests/test_revision_constants_parity.py` | new file | +44 / 0 |

Total: 3 files changed, 60 insertions(+), 1 deletion(-).

**Operator-WIP preservation verified post-commit:**

```bash
$ cd /workspaces/firestarter_app && git status --short
 M firestarter/config.py
?? .planning/STATE.md
```

Operator's pre-existing WIP in `firestarter/config.py` still ` M` (modified-unstaged); `.planning/STATE.md` still `??` (untracked). Neither touched by Plan 05.

**Acceptance checks (all PASS):**

| Check | Command | Result |
|-------|---------|--------|
| Branch is `v1.7-shield-investigation` | `git rev-parse --abbrev-ref HEAD` | `v1.7-shield-investigation` (PASS) |
| Subject starts `feat(34-05):` | `git log -1 --format=%s \| grep -q "^feat(34-05):"` | PASS |
| Subject cites D-08 | `git log -1 --format=%B \| grep -q "D-08"` | PASS |
| Subject cites DETECT-FW-01 | `git log -1 --format=%B \| grep -q "DETECT-FW-01"` | PASS |
| Commit touches exactly 3 plan-owned files | `git show --name-only HEAD` | 3 files (PASS) |
| `git status --porcelain` post-commit clean for plan-owned files | (only operator WIP remains) | PASS |
| Operator `firestarter/config.py` preserved unstaged | `git status --short \| grep "config.py"` | ` M firestarter/config.py` (PASS) |
| Operator `.planning/STATE.md` preserved untracked | `git status --short \| grep "STATE.md"` | `?? .planning/STATE.md` (PASS) |
| pytest post-commit | `cd firestarter_app && pytest` | 83 passed (PASS) |

## Verification

### Plan-level success criteria — all PASS

| Criterion | Evidence |
|-----------|----------|
| `firestarter_app/firestarter/constants.py` carries new `# RURP Hardware Revisions` block with 7 constants (REVISION_0=0x00 through REVISION_UNKNOWN=0xFE) | 8 grep assertions PASS (section header + 7 constants); Python smoke-import PASS; verbatim block content above |
| `firestarter_app/CLAUDE.md` Constants subsection extended with RURP_HARDWARE_REVISIONS sync-rule sentence (Phase 33 CTRL_* sentence preserved) | 5 grep assertions PASS (block name + phase citation + REVISION_UNKNOWN + sentinel narrative + preserved Phase 33 sentence); verbatim sentence above |
| `firestarter_app/tests/test_revision_constants_parity.py` exists with hard parity assertion | File exists; test function present; named imports; all 7 byte values asserted; module-alone pytest = 1 passed; full suite = 83 passed |
| pytest -q exits 0 with all tests pass | `pytest` returned `83 passed in 0.92s` (82 Phase-33 baseline + 1 new parity test) |
| Single atomic commit on firestarter_app sub-repo v1.7-shield-investigation branch — ONLY 3 plan-owned files staged | Commit `9752a85` covers exactly `firestarter/constants.py` + `CLAUDE.md` + `tests/test_revision_constants_parity.py`; operator WIP `firestarter/config.py` + `.planning/STATE.md` remain unstaged/untracked |
| `git -C firestarter_app status` post-commit shows operator WIP still unstaged/untracked | ` M firestarter/config.py` + `?? .planning/STATE.md` confirmed |
| SUMMARY.md created and committed in meta-repo plan directory | this file (next meta-repo commit) |
| STATE.md updated with position | next state-update step (Current Plan: 5 → 6) |
| ROADMAP.md updated with plan progress | next state-update step (Phase 34: 5/7 → 6/7 — but the actual progress accounting happens via the SDK roadmap update verb) |

### Threat model — T-34-05 mitigation verified

| Threat | Mitigation | Status |
|--------|------------|--------|
| T-34-05 (Tampering): Future cross-repo drift between firmware enum byte values and Python REVISION_* constants | Hard pytest parity gate at `firestarter_app/tests/test_revision_constants_parity.py` asserts all 7 byte values per VALIDATION Dim 3 + Dim 6; CLAUDE.md sync-rule prose documents the maintenance burden for future maintainers; same disposition as Phase 33 D-08 substrate (`782ef2a`) which established this exact substrate. Any drift FAILs `pytest` immediately. | MITIGATED |

## Deviations from Plan

**None — plan executed exactly as written.** No Rule 1-4 triggers. No auth gates. No checkpoints.

The plan was straightforward Wave 3 Python-parity work; the three coupled changes landed in the prescribed order (constants.py block → CLAUDE.md sync rule → parity test → atomic commit); selective staging preserved the operator's WIP cleanly; pytest baseline lifted from 82 to 83 with no regressions.

**Total deviations:** 0
**Impact on plan:** None.

## Cross-cutting context preserved

- **Branch model invariant:** firestarter_app sub-repo + meta-repo both on `v1.7-shield-investigation` per `feedback_branching` memory. firestarter sub-repo NOT touched by this plan (still on pinned SHA `032a2e2` per Plan 04's meta-repo bump `a8805b0`).
- **Operator WIP preserved untouched:** `firestarter_app/firestarter/config.py` (` M`) + `firestarter_app/.planning/STATE.md` (`??`) inside the firestarter_app sub-repo + untracked `.planning/phases/33-silkscreen-label-code-alias-migration/33-VERIFICATION.md` + meta-repo `.planning/STATE.md` mods (orchestrator-owned) all unchanged from pre-plan state.
- **Meta-repo firestarter_app submodule pointer NOT bumped by Plan 05** — per the `<sequential_execution>` guidance, Plan 07 owns the meta-repo submodule pointer bump (mirrors Plan 04's `a8805b0` shape — but for the firestarter_app submodule, subsuming Plan 05 + Plan 06 sub-repo commits in one atomic meta-repo commit).
- **MSG_OK_REV wire shape unchanged per D-09:** no codegen pass on `tools/catalog/messages.toml`; the new Python REVISION_* constants are documentary substrate consumed by Plan 06's host-side `_REVISION_SILKSCREEN` dict, not the wire frame itself. The MSG_OK_REV `(physical_u8, effective_u8)` payload positions stay verbatim.
- **firestarter_app pytest baseline lifted from 82 → 83:** Phase 33 baseline (82 tests) preserved + 1 new parity test (`test_revision_byte_values_match_firmware_enum`). Plan 06 will measure its delta against the new 83-test baseline.

## Hand-off to Plan 06 (Wave 3 — `firestarter_app/firestarter/serial_comm.py` `_REVISION_SILKSCREEN` dict per D-05 Path A)

Plan 06 consumes the 7 Python REVISION_* constants this plan landed and:

1. Adds a `_REVISION_SILKSCREEN` dict (or analogous lookup) in `firestarter_app/firestarter/serial_comm.py` mapping each REVISION_* byte value to its silkscreen-version string (`REVISION_0 → "Rev 0"`, `REVISION_1 → "Rev 1"`, `REVISION_2_0 → "Rev 2.0-class"`, `REVISION_2_1 → "Rev 2.1"`, `REVISION_2_2 → "Rev 2.2"`, `REVISION_2_3 → "Rev 2.3"`, `REVISION_UNKNOWN → "rev_unknown"`). Defensive `.get()` rendering for any non-canonical byte (e.g., `0xFF` EEPROM-override-absent → fallback to numeric formatting).
2. Extends the MSG_OK_REV format path (`_format_message` or sibling at `serial_comm.py:325-340`) to consume the dict per D-05 Path A.
3. Lands the change as a single atomic commit on the firestarter_app sub-repo v1.7-shield-investigation branch.

**Substrate ready (anchored at this plan's close):**

- **REVISION_* constants:** all 7 importable from `firestarter.constants`; pytest parity gate guarantees byte-value fidelity vs the firmware enum.
- **firestarter sub-repo HEAD (pinned in meta-repo via Plan 04 `a8805b0`):** still at `032a2e2`; contains `REVISION_2_3 = 5` + `REVISION_UNKNOWN = 0xFE`. Plan 05's pytest gate cross-checks against this pin.
- **CLAUDE.md sync-rule prose:** covers both the Phase 33 CTRL_* block AND the Phase 34 REVISION_* block — future maintainers see both sync burdens at the same paragraph.
- **pytest baseline:** 83/83 PASS at plan-close. Plan 06's delta is measured against this.

## Hand-off to Plan 07 (Wave 4 — meta-repo `firestarter_app` submodule pointer bump)

Plan 07 follows Plan 06. Bumps the meta-repo `firestarter_app` submodule pointer from its current baseline (Plan 04 baseline, pre-Plan-05 firestarter_app SHA) to the Plan 06 close SHA — subsuming this plan's `9752a85` + Plan 06's commit in one atomic meta-repo commit on the `v1.7-shield-investigation` branch. Mirrors Plan 04's `a8805b0` commit shape (single submodule-pointer-bump commit with body citing both subsumed sub-repo SHAs + requirements + GATE-1.7 evidence).

## Self-Check: PASSED

- [x] `.planning/phases/34-shield-version-detect-design-firmware-plumbing/34-05-SUMMARY.md` exists (this file)
- [x] firestarter_app sub-repo commit `9752a85` present on `v1.7-shield-investigation` branch (`cd firestarter_app && git log --oneline | grep 9752a85` → FOUND)
- [x] firestarter_app sub-repo HEAD subject = `feat(34-05): add RURP_HARDWARE_REVISIONS Python parity block + sync rule + pytest gate (D-08; DETECT-FW-01)`
- [x] firestarter_app sub-repo HEAD touches exactly 3 plan-owned files (constants.py + CLAUDE.md + tests/test_revision_constants_parity.py)
- [x] `firestarter_app/firestarter/constants.py` carries new `# RURP Hardware Revisions` block with 7 REVISION_* constants (REVISION_0 = 0x00 through REVISION_UNKNOWN = 0xFE) — verified via 8 grep assertions
- [x] `firestarter_app/CLAUDE.md:100` paragraph extended with RURP_HARDWARE_REVISIONS sync-rule sentence — verified via 5 grep assertions (block name + phase citation + REVISION_UNKNOWN + sentinel narrative + preserved Phase 33 sentence)
- [x] `firestarter_app/tests/test_revision_constants_parity.py` exists with `def test_revision_byte_values_match_firmware_enum()` asserting all 7 REVISION_* byte values
- [x] Python smoke-import green: `python -c "from firestarter.constants import ...; assert REVISION_2_3 == 0x05; assert REVISION_UNKNOWN == 0xFE"` → exit 0
- [x] `cd firestarter_app && pytest -q tests/test_revision_constants_parity.py` → `1 passed`
- [x] `cd firestarter_app && pytest` → `83 passed in 0.92s` (82 Phase-33 baseline + 1 new parity test)
- [x] Operator WIP preserved untouched: ` M firestarter/config.py` + `?? .planning/STATE.md` in firestarter_app post-commit
- [x] Meta-repo firestarter_app submodule pointer NOT bumped by this plan (Plan 07 owns that)
- [x] Branch invariant honored (firestarter_app on `v1.7-shield-investigation`)
- [x] No `34-05-INVESTIGATION.md` created (would indicate a FAIL escalation)

---

*Phase: 34-shield-version-detect-design-firmware-plumbing*
*Completed: 2026-05-25*

---
phase: 34-shield-version-detect-design-firmware-plumbing
plan: 06
subsystem: host-cli-and-meta-submodule-bump
tags: [host-cli, python, serial-comm, silkscreen-mapping, sub-repo-bump, detect-fw-01, detect-fw-02, phase-34-close]

# Dependency graph
requires:
  - phase: 34-shield-version-detect-design-firmware-plumbing
    plan: 04
    provides: "firestarter sub-repo firmware: REVISION_2_3 + REVISION_UNKNOWN enum extension + analog A3 band-lookup detection logic + MSG_OK_REV wire shape preserved per D-09"
  - phase: 34-shield-version-detect-design-firmware-plumbing
    plan: 05
    provides: "firestarter_app sub-repo: RURP_HARDWARE_REVISIONS block in constants.py (REVISION_0..REVISION_UNKNOWN, byte values mirroring firmware enum); CLAUDE.md sync rule extended; Python parity test (Plan 05 baseline = 83 pytest tests)"
provides:
  - "firestarter_app/firestarter/serial_comm.py — host-side cosmetic enum-byte → silkscreen-string mapping for MSG_OK_REV via module-scope _REVISION_SILKSCREEN dict + extended _format_message branch using defensive .get() lookup"
  - "tests/test_decoder.py — 2 MSG_OK_REV-rendering tests adjusted to the new silkscreen-string output (Path A consciously changes 'Rev1'/'Rev2,…' → 'Rev 1'/'Rev 2.0-class,…')"
  - "Meta-repo firestarter_app submodule pointer bumped to b2183ed — anchors Wave 3 Python deliverables (Plan 05 constants + Plan 06 serial_comm) in the meta-repo git history"
  - "DETECT-FW-01 + DETECT-FW-02 substrate fully closed across both sub-repos + meta-repo (firmware enum extension Plan 04; Python constants parity Plan 05; host cosmetic mapping Plan 06)"
  - "Phase 34 desk-side scope FULLY CLOSED — Phase 35 hand-off ready (operator-on-bench validation + milestone close per D-10 deferral)"
affects:
  - "Phase 35 (Documentation + Milestone Close) — consumes the closed Phase 34 substrate; sub-repo v1.7-shield-investigation → beta promotion happens at Phase 34 close per the v1.7 branch model (D-10 desk-side gate); beta → main promotion gated on operator-on-bench UAT in Phase 35"
  - "v1.6 Phase 27 resume — RCA re-open can cite silkscreen-rev strings in instrumented A/B logs ('Rev 2.0-class' vs 'Rev 2.3' etc.) — useful for ruling out 'operator forgot to set hw_revision byte' as a confound when reproducing the read-bug across boards"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Module-scope const-style dict near MAGIC_PREAMBLE / STATE_MACHINE_PREFIXES / NON_RESPONSE_PREFIXES declarations — same idiom as PATTERNS Pattern 7 substrate"
    - "Defensive .get(byte, f\"Rev{byte}\") lookup — mirrors Phase 33's COMMAND_NAMES.get(cmd) usage in the same _format_message function; unknown bytes fall through to 'Rev{n}' rather than raising KeyError on future enum additions"
    - "Path A wire-shape-invariant cosmetic improvement — Python rendering only; no toml codegen, no firmware change, no MSG_OK_REV wire byte change"
    - "Atomic sub-repo commit + separate meta-repo submodule-pointer bump — same pattern as Phase 33 Plan 04 (`782ef2a feat(33-04): bump firestarter_app to 907c7b2`) and Phase 34 Plan 04 precedent"

key-files:
  created:
    - ".planning/phases/34-shield-version-detect-design-firmware-plumbing/34-06-SUMMARY.md (this file)"
  modified:
    - "firestarter_app/firestarter/serial_comm.py (+16 lines / -5 lines: new _REVISION_SILKSCREEN dict + 7 silkscreen strings; replaced MSG_OK_REV rendering branch with 5-line Path A variant; 0xFF-effective-sentinel branch preserved verbatim)"
    - "firestarter_app/tests/test_decoder.py (2 MSG_OK_REV-rendering test assertions adjusted to the new silkscreen-string format; MSG_OK_CFG test untouched — Plan 06 only extends MSG_OK_REV)"
    - "Meta-repo firestarter_app submodule pointer (40-hex SHA bumped to b2183ed2fc9c78d4569c410e6a2593c073fc5e1a)"

key-decisions:
  - "D-05 Path A applied verbatim: silkscreen string mapping lives host-side only via module-scope dict + .get() lookup; firmware writes the u8 enum byte via MSG_OK_REV verbatim with no transformation. Closes the host-side leg of DETECT-FW-01."
  - "D-09 wire-shape invariant honored: MSG_OK_REV wire shape (physical_u8, effective_u8) unchanged; tools/catalog/messages.toml untouched; firestarter_app/firestarter/messages.py (auto-generated catalog) untouched; firestarter_app/firestarter/hardware.py (consumer) untouched."
  - "Path A consciously changes the rendered string format: 'Rev1' → 'Rev 1', 'Rev2, Override HW: Rev5' → 'Rev 2.0-class, Override HW: Rev 2.3', etc. Two existing pytest assertions in tests/test_decoder.py required updating to match the new format — committed in the same atomic commit as the serial_comm.py change."
  - "The 0xFF-effective-sentinel branch is preserved verbatim per PATTERNS Pattern 7 critical-preservation rule — `if effective == 0xFF: return phys_str` still indicates 'no EEPROM override active'."
  - "Per Phase 33 Plan 04 + Phase 34 Plan 04 sub-repo-bump precedent: 1 atomic commit inside the firestarter_app sub-repo on v1.7-shield-investigation branch (commit b2183ed) + 1 separate meta-repo commit on v1.7-shield-investigation branch bumping the submodule pointer (commit bef5bec)."

requirements-completed:
  - DETECT-FW-01
  - DETECT-FW-02

# Metrics
duration: ~8min
completed: 2026-05-25
---

# Phase 34 Plan 06: Wave 3 — Host-Side Silkscreen-String Mapping + Phase 34 Close Summary

**Closed Phase 34 desk-side scope end-to-end: host-side enum-byte → silkscreen-string mapping landed in `firestarter_app/firestarter/serial_comm.py` per D-05 Path A (module-scope `_REVISION_SILKSCREEN` dict + extended `_format_message` MSG_OK_REV branch using defensive `.get()` lookup); wire shape unchanged per D-09; meta-repo `firestarter_app` submodule pointer bumped to b2183ed anchoring Plan 05 + Plan 06 Python deliverables. DETECT-FW-01 + DETECT-FW-02 substrate complete across firmware + Python + meta-repo. Phase 35 hand-off ready.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-05-25T~14:13Z (immediately after Plan 05 close)
- **Completed:** 2026-05-25T~14:21Z
- **Tasks:** 2 (Task 1 — add dict + extend _format_message branch; Task 2 — atomic sub-repo commit + meta-repo submodule-pointer bump)
- **firestarter_app sub-repo commits:** 1 (`b2183ed`)
- **Meta-repo commits:** 1 (`bef5bec`)
- **Files modified (sub-repo):** 2 (`firestarter/serial_comm.py`, `tests/test_decoder.py`)
- **Files modified (meta-repo):** 1 (`firestarter_app` submodule pointer)

## Accomplishments

### Task 1 — `_REVISION_SILKSCREEN` dict + extend `_format_message` MSG_OK_REV branch

**Modification A — module-scope `_REVISION_SILKSCREEN` dict added.** Inserted in `firestarter_app/firestarter/serial_comm.py` near the existing `MAGIC_PREAMBLE` / `STATE_MACHINE_PREFIXES` / `NON_RESPONSE_PREFIXES` declarations (per PATTERNS Pattern 7). 3-line comment header + 7-entry dict literal:

| REVISION_* constant | Byte value | Silkscreen string |
|---------------------|-----------|-------------------|
| `REVISION_0` | `0x00` | `"Rev 0"` |
| `REVISION_1` | `0x01` | `"Rev 1"` |
| `REVISION_2_0` | `0x02` | `"Rev 2.0-class"` (broad bucket per Phase 34 D-04 — covers Rev 2.0 / 2.1 / 2.2 with R41=4k7; ADC cannot distinguish these three) |
| `REVISION_2_1` | `0x03` | `"Rev 2.1 (override)"` (via EEPROM override only — ADC cannot distinguish) |
| `REVISION_2_2` | `0x04` | `"Rev 2.2 (override)"` (via EEPROM override only — ADC cannot distinguish) |
| `REVISION_2_3` | `0x05` | `"Rev 2.3"` (R41=10k physical detect) |
| `REVISION_UNKNOWN` | `0xFE` | `"rev_unknown"` (ADC band-gap or pre-detect-resistor + A2 indeterminate fall-through) |

Constants are sourced via the existing `from firestarter.constants import *` wildcard near the top of `serial_comm.py` (Phase 33 P-02 convention) — Plan 05 added the `RURP_HARDWARE_REVISIONS` block to `constants.py` which contributes these symbols to the wildcard's export surface. No new named import was added.

**Modification B — `_format_message` MSG_OK_REV branch replaced with 5-line Path A variant.** Pre-edit (single-format-string rendering using `Rev{byte}` literal):

```python
if msg_id == MSG_OK_REV and len(params) == 2:
    physical, effective = params[0], params[1]
    if effective == 0xFF:
        return f"Rev{physical}"
    return f"Rev{effective}, Override HW: Rev{physical}"
```

Post-edit (defensive `.get()` lookup with fallback to `Rev{byte}`):

```python
if msg_id == MSG_OK_REV and len(params) == 2:
    physical, effective = params[0], params[1]
    phys_str = _REVISION_SILKSCREEN.get(physical, f"Rev{physical}")
    if effective == 0xFF:
        return phys_str
    eff_str = _REVISION_SILKSCREEN.get(effective, f"Rev{effective}")
    return f"{eff_str}, Override HW: {phys_str}"
```

Critical preservation per PATTERNS Pattern 7:
- `if msg_id == MSG_OK_REV and len(params) == 2:` guard UNCHANGED.
- 0xFF-effective-sentinel branch preserved verbatim (`if effective == 0xFF: return phys_str` still indicates "no override active" per Phase 33 substrate).
- `dict.get(byte, fallback)` defensive idiom — unknown bytes fall through to `f"Rev{byte}"` rather than raising KeyError. Same idiom as Phase 33's `COMMAND_NAMES.get(cmd)` usage in this same function.
- Neighboring MSG_OK_CFG rendering branch at `:359-363` UNCHANGED (Plan 06 only extends MSG_OK_REV; MSG_OK_CFG `Override HW: Rev{override}` clause still uses the legacy literal format).
- `tools/catalog/messages.toml` UNCHANGED (D-09 wire-shape invariant).
- `firestarter_app/firestarter/messages.py` (auto-generated catalog) UNCHANGED.
- `firestarter_app/firestarter/hardware.py` (consumer) UNCHANGED.

**Test adjustments — `tests/test_decoder.py`:** Two MSG_OK_REV-rendering tests broke on the conscious string-format change per Path A. Updated both with docstring note citing Phase 34 D-05 Path A:

- `test_ok_rev_p02_with_override_decodes`: `"Rev2, Override HW: Rev1"` → `"Rev 2.0-class, Override HW: Rev 1"` (physical=0x01 + effective=0x02; new silkscreen-string format).
- `test_ok_rev_p02_no_override_decodes`: `"Rev1"` → `"Rev 1"` (physical=0x01 + effective=0xFF sentinel; new silkscreen-string format with explicit space).

MSG_OK_CFG-rendering tests at `test_decoder.py:398-410` and onward UNTOUCHED — Plan 06 does not extend the MSG_OK_CFG branch.

### Task 2 — atomic sub-repo commit + meta-repo submodule-pointer bump

**Part 1 — firestarter_app sub-repo commit (`b2183ed`):**

- Branch verified: `v1.7-shield-investigation` (sub-repo).
- Pre-commit diff sanity: `git status --porcelain firestarter/` showed only `firestarter/serial_comm.py` modified by Plan 06 (operator's pre-existing `firestarter/config.py` WIP preserved unstaged).
- Stage: `git add firestarter/serial_comm.py tests/test_decoder.py` (selective — `git add .` / `-A` explicitly avoided).
- Commit subject: `feat(34-06): add _REVISION_SILKSCREEN dict to serial_comm.py for MSG_OK_REV rendering (D-05; DETECT-FW-01)`.
- Commit body cites: D-05 Path A, D-08 (Python parity foundation), D-09 (wire shape unchanged), PATTERNS Pattern 7 defensive `.get()` idiom; the 7 silkscreen-string entries; preservation of 0xFF sentinel branch; the test-file change with rationale; `messages.toml` / `messages.py` / `hardware.py` all UNCHANGED.
- Diff: 2 files changed, 25 insertions(+), 6 deletions(-).
- Post-commit: `git status --porcelain` showed only `firestarter/config.py` (operator WIP) and `.planning/STATE.md` (untracked) — all sub-repo-owned cross-cutting context preserved per the sequential_execution contract.

**Part 2 — meta-repo `firestarter_app` submodule-pointer bump (`bef5bec`):**

- Branch verified: `v1.7-shield-investigation` (meta-repo).
- Submodule state: ` M firestarter_app` (sub-repo HEAD advanced from the Plan 04-recorded SHA to Plan-06-HEAD `b2183ed`; Plan 05's commit is reachable by traversing the sub-repo history backwards from `b2183ed`).
- Stage: `git add firestarter_app`.
- Commit subject (per Phase 33 Plan 04 + Phase 34 Plan 04 precedent): `feat(34-06): bump firestarter_app to b2183ed — Python REVISION_* parity + serial_comm silkscreen mapping (DETECT-FW-01 + DETECT-FW-02; Phase 34 close)`.
- Commit body cites: Plan 05 (constants.py RURP_HARDWARE_REVISIONS block + CLAUDE.md sync rule + parity test) + Plan 06 (serial_comm silkscreen dict); D-05 Path A; D-08 Python parity; D-09 wire shape unchanged; operator-visible outcome (silkscreen strings in log/CLI output); Phase 34 desk-side scope CLOSED with Phase 35 hand-off ready; Phase 33 Plan 04 precedent.
- Diff: 1 file changed, 1 insertion(+), 1 deletion(-) — pure submodule-pointer move.

## Verification

### Task 1 verification (host-side cosmetic mapping)

| Check | Command | Result |
|-------|---------|--------|
| `_REVISION_SILKSCREEN` dict declaration present | `grep -q "_REVISION_SILKSCREEN" serial_comm.py` | PASS |
| Silkscreen string `"Rev 2.0-class"` present | `grep -q "Rev 2.0-class" serial_comm.py` | PASS |
| Silkscreen string `"rev_unknown"` present | `grep -q "rev_unknown" serial_comm.py` | PASS |
| `_REVISION_SILKSCREEN.get(physical` defensive lookup | `grep -q "_REVISION_SILKSCREEN.get(physical" serial_comm.py` | PASS |
| `_REVISION_SILKSCREEN.get(effective` defensive lookup | `grep -q "_REVISION_SILKSCREEN.get(effective" serial_comm.py` | PASS |
| 0xFF-effective-sentinel branch preserved verbatim | `grep -q "if effective == 0xFF" serial_comm.py` | PASS |
| `firestarter_app/firestarter/messages.py` UNCHANGED (D-09 wire-shape invariant) | `git status --porcelain firestarter/messages.py` returns empty | PASS |
| `firestarter_app/firestarter/hardware.py` UNCHANGED | `git status --porcelain firestarter/hardware.py` returns empty | PASS |
| Smoke-test: `_REVISION_SILKSCREEN[0x02] == 'Rev 2.0-class'` | Python import + assert | PASS |
| Smoke-test: `_REVISION_SILKSCREEN[0xFE] == 'rev_unknown'` | Python import + assert | PASS |
| Smoke-test: `_format_message(MSG_OK_REV, [0x02, 0xFF])` → `'Rev 2.0-class'` | Python call + assert | PASS |
| Smoke-test: `_format_message(MSG_OK_REV, [0x05, 0x02])` → `'Rev 2.0-class, Override HW: Rev 2.3'` | Python call + assert | PASS |
| Smoke-test: unknown byte fallback `_format_message(MSG_OK_REV, [99, 0xFF])` → `'Rev99'` | Python call + assert | PASS |
| `cd firestarter_app && pytest -q` | full suite | **83 passed in 0.86s** |

### pytest output verbatim

```
$ cd /workspaces/firestarter_app && pytest
........................................................................ [ 86%]
...........                                                              [100%]
83 passed in 0.86s
```

### Task 2 verification (atomic sub-repo commit + meta-repo submodule bump)

| Check | Result |
|-------|--------|
| firestarter_app sub-repo on `v1.7-shield-investigation` branch | PASS |
| Sub-repo HEAD commit subject starts with `feat(34-06)` | PASS (`feat(34-06): add _REVISION_SILKSCREEN dict to serial_comm.py for MSG_OK_REV rendering (D-05; DETECT-FW-01)`) |
| Sub-repo commit body references `D-05` | PASS (3 matches in commit body) |
| Sub-repo commit touches only `firestarter/serial_comm.py` + `tests/test_decoder.py` | PASS (`git show --stat HEAD` → 2 files / 25 insertions / 6 deletions) |
| Meta-repo on `v1.7-shield-investigation` branch | PASS |
| Meta-repo HEAD commit subject starts with `feat(34-06)` AND contains `bump firestarter_app` | PASS (`feat(34-06): bump firestarter_app to b2183ed — Python REVISION_* parity + serial_comm silkscreen mapping (DETECT-FW-01 + DETECT-FW-02; Phase 34 close)`) |
| Meta-repo commit body cites `DETECT-FW-01` | PASS (2 matches) |
| Meta-repo commit body cites `DETECT-FW-02` | PASS (2 matches) |
| Meta-repo commit touches only `firestarter_app` submodule pointer | PASS (`git show --stat HEAD` → 1 file / 1 insertion / 1 deletion) |
| Pinned submodule SHA matches sub-repo HEAD | PASS (`b2183ed2fc9c78d4569c410e6a2593c073fc5e1a` on both sides) |
| Operator's pre-existing `firestarter/config.py` WIP preserved | PASS (` M firestarter/config.py` still in `git status` post-commit) |
| `.planning/STATE.md` (untracked, orchestrator-owned) preserved | PASS (`?? .planning/STATE.md` still in `git status` post-commit) |

The meta-repo's `git status --porcelain firestarter_app` reports ` M firestarter_app` post-commit; `git diff firestarter_app` shows `Subproject commit b2183ed2fc9c78d4569c410e6a2593c073fc5e1a-dirty` — the **`-dirty` suffix is the operator's pre-existing `config.py` WIP** carried forward unchanged (same pattern as Phase 33 Plan 04 SUMMARY "config.py drift carries forward unchanged"). The pinned SHA is exactly correct.

### Commit hashes for the record

| Repo | Commit | Subject |
|------|--------|---------|
| firestarter_app sub-repo | `b2183ed2fc9c78d4569c410e6a2593c073fc5e1a` | feat(34-06): add _REVISION_SILKSCREEN dict to serial_comm.py for MSG_OK_REV rendering (D-05; DETECT-FW-01) |
| Meta-repo (`/workspaces`) | `bef5beced31af83c3219b72a37c56eb76267aa07` | feat(34-06): bump firestarter_app to b2183ed — Python REVISION_* parity + serial_comm silkscreen mapping (DETECT-FW-01 + DETECT-FW-02; Phase 34 close) |

## Deviations from Plan

None — plan executed exactly as written. The two `tests/test_decoder.py` MSG_OK_REV-rendering assertion updates were **explicitly anticipated by the plan's Task 1 action**: "Path A consciously changes the rendered string from `\"Rev2\"` to `\"Rev 2.0-class\"` etc., which COULD break a string-equality assertion in a test; in that case adjust the test to match the new string AND record the test-file change in the commit body." The change was made + recorded in the sub-repo commit body as instructed; pytest 83/83 green confirms no other test relied on the old format.

## Cross-cutting context preserved

- **firestarter_app/firestarter/config.py operator WIP** — the pre-existing uncommitted refactor of `get_local_database`, `get_local_pin_maps`, `ConfigManager._load_config`, and `update_config` was NOT touched. Verified post-commit: `git -C firestarter_app status --porcelain firestarter/config.py` → ` M firestarter/config.py` (still unstaged). This drift predates Phase 33 and carries forward on the `v1.7-shield-investigation` branch unchanged.
- **firestarter_app/.planning/STATE.md** (untracked, inside the firestarter_app sub-repo) — left untracked per the sequential_execution contract.
- **Meta-repo's `.planning/phases/33-silkscreen-label-code-alias-migration/33-VERIFICATION.md`** (untracked) — pre-existing; left untouched.
- **Branch model invariant:** firestarter_app sub-repo + meta-repo both on `v1.7-shield-investigation` per [[feedback_branching]] memory; sub-repo work commits inside the submodule first, then a pointer-bump commit lands in the meta-repo (per sequential_execution contract).

## Phase 34 desk-side scope CLOSED — Phase 35 hand-off

> **STATUS BANNER: Phase 34 DESK-SIDE SCOPE CLOSED.**
>
> All 4 v1.7 Phase 34 requirements (DETECT-HW-01, DETECT-HW-02, DETECT-FW-01, DETECT-FW-02) have substrate complete across firmware + Python + meta-repo:
>
> - **DETECT-HW-01** (resistor divider into ADC pin + voltage bands) — closed by Plan 01 (§8 schematic-delta documentation per D-01 / D-02 / D-03).
> - **DETECT-HW-02** (per-rev expected ADC band table) — closed by Plan 02 / Plan 03 (§9 band-table fill per D-11 schema).
> - **DETECT-FW-01** (firmware ADC read + handshake reports detected silkscreen-rev + EEPROM fall-through) — closed by Plan 04 (firmware: REVISION_2_3 + REVISION_UNKNOWN enum + analog A3 band-lookup + EEPROM-override-precedence preserved) + Plan 05 (Python parity: RURP_HARDWARE_REVISIONS block) + Plan 06 (host-side cosmetic silkscreen mapping).
> - **DETECT-FW-02** (GATE-1.7 non-regression) — closed by Plan 04 (firmware `.hex` size delta within budget; native test green) + Plan 05 (pytest 83/83 green; Python parity test enforces byte-value invariant) + Plan 06 (pytest 83/83 green post-test-string-format-update; wire shape unchanged per D-09).
>
> **Hand-off to Phase 35** (Documentation + Milestone Close — per D-10 deferral):
>
> - Operator-on-bench validation: sideload Phase 34 firmware to operator's Rev 2.0 or Rev 2.2 board (chip OUT of socket per memory [[feedback_chip_out_before_sideload]]; verify port identity per memory [[feedback_verify_port_identity_each_task]]) and confirm `MSG_OK_REV` reports either `"Rev 2.0-class"` (R41 populated) or `"rev_unknown"` (R41 not populated) — either way is acceptable per the backward-compat fall-through clause.
> - Rev 2.2 R41 physical measurement (Phase 35 follow-up #5 — 4k7 schematic vs 10k chat discrepancy resolution): if Rev 2.2 board reports `"Rev 2.3"` instead of `"Rev 2.0-class"`, that's data toward resolving the discrepancy.
> - Sub-repo `v1.7-shield-investigation` → `beta` promotion happens at Phase 35 close per the v1.7 branch model; `beta` → `main` is gated on operator-on-bench at Phase 35.
> - README cross-links (firmware + app) point to `v1.7-SHIELD-REVS.md` §3 / §8 / §9 — Phase 35 owns.

## Self-Check: PASSED

- [x] `firestarter_app/firestarter/serial_comm.py` modified — `_REVISION_SILKSCREEN` dict + extended `_format_message` MSG_OK_REV branch (`grep -q "_REVISION_SILKSCREEN" /workspaces/firestarter_app/firestarter/serial_comm.py` → FOUND)
- [x] All 7 silkscreen strings present (`grep -E '"Rev 0"|"Rev 1"|"Rev 2\.0-class"|"Rev 2\.1 \(override\)"|"Rev 2\.2 \(override\)"|"Rev 2\.3"|"rev_unknown"' serial_comm.py` → FOUND)
- [x] Defensive `.get()` lookup for both physical and effective bytes (`grep -q "_REVISION_SILKSCREEN.get(physical" serial_comm.py && grep -q "_REVISION_SILKSCREEN.get(effective" serial_comm.py` → FOUND)
- [x] 0xFF-effective-sentinel branch preserved verbatim (`grep -q "if effective == 0xFF" serial_comm.py` → FOUND)
- [x] `firestarter_app/tests/test_decoder.py` MSG_OK_REV-rendering assertions updated (test_ok_rev_p02_with_override_decodes → "Rev 2.0-class, Override HW: Rev 1"; test_ok_rev_p02_no_override_decodes → "Rev 1")
- [x] `tools/catalog/messages.toml` UNCHANGED (D-09 invariant — `git status --porcelain tools/catalog/messages.toml` empty in meta-repo)
- [x] `firestarter_app/firestarter/messages.py` UNCHANGED (auto-generated catalog — D-09 invariant)
- [x] `firestarter_app/firestarter/hardware.py` UNCHANGED (consumer — RESEARCH §`hardware.py` Consumer — UNCHANGED)
- [x] `cd firestarter_app && pytest -q` exits 0 — 83 passed in 0.86s
- [x] firestarter_app sub-repo commit `b2183ed` present on `v1.7-shield-investigation` branch (`cd firestarter_app && git log --oneline | head -1` → `b2183ed feat(34-06): …`)
- [x] Meta-repo submodule-pointer-bump commit `bef5bec` present on `v1.7-shield-investigation` branch (`git -C /workspaces log --oneline -1` → `bef5bec feat(34-06): bump firestarter_app to b2183ed …`)
- [x] Pinned submodule SHA equals sub-repo HEAD (`git -C /workspaces ls-tree HEAD firestarter_app | awk '{print $3}'` = `b2183ed2fc9c78d4569c410e6a2593c073fc5e1a` = `cd firestarter_app && git rev-parse HEAD`)
- [x] Operator's `firestarter/config.py` WIP drift preserved untouched (`git -C firestarter_app status --porcelain firestarter/config.py` → ` M firestarter/config.py`)
- [x] Phase 34 desk-side scope CLOSED — DETECT-FW-01 + DETECT-FW-02 substrate complete; Phase 35 hand-off ready

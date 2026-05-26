---
phase: 35-documentation-milestone-close
plan: 02
subsystem: api
tags: [serial-protocol, message-catalog, silkscreen-rendering, host-cli, pytest, tdd]

# Dependency graph
requires:
  - phase: 34-shield-version-detect-design-firmware-plumbing
    provides: "_REVISION_SILKSCREEN dict (Phase 34 D-05) + MSG_OK_REV silkscreen branch + REVISION_* enum bytes on both firmware and host"
provides:
  - "MSG_INFO_HW (0x5B) silkscreen-aware rendering — REVISION_UNKNOWN (0xFE) now surfaces as 'HW: rev_unknown' instead of 'HW: Rev254'"
  - "MSG_INFO_PHYSICAL_HW (0x5C) silkscreen-aware rendering — same mapping with 'Physical HW: ' prefix"
  - "MSG_OK_CFG Override clause silkscreen-aware rendering — byte 0x02 surfaces as 'Override HW: Rev 2.0-class' instead of 'Override HW: Rev2'"
  - "WR-01 + WR-02 from 34-REVIEW.md closed — all 4 silkscreen surfaces agree on the same revision byte"
  - "7 new pytest cases covering REVISION_1 / REVISION_UNKNOWN / unknown-byte fallback paths"
affects:
  - "35-03 (meta-repo submodule pointer bump — Plan 03 owns the pointer move)"
  - "Phase 35 Wave 2 bench UAT — operator's boot log no longer contradicts MSG_OK_REV ack"
  - "Plan 35-01 firmware CR-02 hard-fail-loud emit — boot-time WARN surfaces with silkscreen string"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-message-ID branch surface in _format_message — same dict-lookup-with-fallback shape across MSG_OK_REV (Phase 34), MSG_OK_CFG override clause, MSG_INFO_HW, MSG_INFO_PHYSICAL_HW"
    - "Defensive .get(byte, f'Rev{byte}') fallback preserves no-space 'Rev{n}' shape so unknown bytes degrade gracefully — mirrors the existing MSG_OK_REV fallback shape"
    - "TDD RED/GREEN per task with separate commits — failing test commit then implementation commit, both with explicit refs to 34-REVIEW.md WR-01/WR-02 + 35-CONTEXT.md D-03/D-04"

key-files:
  created: []
  modified:
    - "firestarter_app/firestarter/serial_comm.py — 2-line import extension + 2 new branches in _format_message + 1-line edit to existing MSG_OK_CFG branch + docstring extension citing Phase 35 D-03/D-04"
    - "firestarter_app/tests/test_decoder.py — 2-line import extension + 7 new tests (6 MSG_INFO_HW/PHYSICAL_HW silkscreen + 1 MSG_OK_CFG unknown-override fallback) + assertion flip on existing test_ok_cfg_p03_with_override_decodes"

key-decisions:
  - "Frame-driven test path used (not direct _format_message call) — INFO-severity frames flow through Response cleanly via the existing _read_and_parse_lines yield surface, same shape as MSG_OK_REV / MSG_INFO_ADDR tests already in the file. No private-method testing needed."
  - "Test naming: test_info_hw_silkscreen_*_decodes (3 cases per message: known_rev / rev_unknown / unknown_byte_falls_back). Matches the descriptive-test-name pattern used elsewhere in test_decoder.py."
  - "Docstring extension on _format_message updated alongside the new branches — single source of truth for the conditional-rendering contract."

patterns-established:
  - "Silkscreen-surface unification — all 4 message surfaces (MSG_OK_REV, MSG_OK_CFG override, MSG_INFO_HW, MSG_INFO_PHYSICAL_HW) consume _REVISION_SILKSCREEN via .get(byte, f'Rev{byte}') for consistent operator-facing rendering"
  - "TDD-per-task within a multi-task plan — Task 1 RED+GREEN as two commits, Task 2 RED+GREEN as two commits; Task 3 verification-only (no new code, full pytest sweep)"

requirements-completed: [DOC-01]

# Metrics
duration: ~15min
completed: 2026-05-25
---

# Phase 35 Plan 02: WR-01 + WR-02 Silkscreen Rendering — Close Phase 34 Host-Side Review Findings Summary

**Routed MSG_INFO_HW, MSG_INFO_PHYSICAL_HW, and the MSG_OK_CFG Override clause through `_REVISION_SILKSCREEN` so all four host silkscreen surfaces render the same revision byte identically — closing WR-01 + WR-02 from `34-REVIEW.md` ahead of the v1.7 sub-repo `beta` promotion.**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-05-25T20:53:30Z (approx)
- **Completed:** 2026-05-25T21:08:28Z
- **Tasks:** 3 (Task 1 + Task 2 TDD RED/GREEN; Task 3 full-pytest verification)
- **Files modified:** 2 (both in `firestarter_app` submodule on `v1.7-shield-investigation`)

## Accomplishments

- **WR-01 closed** — `_format_message` now has two new branches for `MSG_INFO_HW` (0x5B) + `MSG_INFO_PHYSICAL_HW` (0x5C); both route the single u8 revision byte through `_REVISION_SILKSCREEN.get(byte, f"Rev{byte}")`, preserving the catalog format strings' `"HW: "` / `"Physical HW: "` prefixes. `REVISION_UNKNOWN` (0xFE) now surfaces as `"HW: rev_unknown"` instead of `"HW: Rev254"`.
- **WR-02 closed** — The MSG_OK_CFG Override clause uses the same `_REVISION_SILKSCREEN.get()` lookup. Byte 0x02 (`REVISION_2_0`) now renders as `"Override HW: Rev 2.0-class"` instead of `"Override HW: Rev2"`, matching the MSG_OK_REV rendering of the same byte.
- **All 4 silkscreen surfaces agree** — `MSG_OK_REV`, `MSG_OK_CFG` override clause, `MSG_INFO_HW`, and `MSG_INFO_PHYSICAL_HW` all consume `_REVISION_SILKSCREEN` via the same `.get(byte, f"Rev{byte}")` pattern.
- **7 new pytest cases** — 6 covering MSG_INFO_HW / MSG_INFO_PHYSICAL_HW (REVISION_1 / REVISION_UNKNOWN / unknown-byte each) + 1 new MSG_OK_CFG unknown-override fallback case + existing `test_ok_cfg_p03_with_override_decodes` flipped to the silkscreen string.
- **Pytest suite total: 90 PASS** (was 83 prior to this plan; +7 net new tests; existing tests unchanged in behavior).
- **Wire format invariant preserved** — Phase 34 D-09 lock honored. Zero changes to `firestarter_app/firestarter/messages.py`; firmware-side `LOG_INFO_ID_U8(...)` / `LOG_OK_ID_*(MSG_OK_CFG, ...)` call sites stay byte-identical.

## Task Commits

Each TDD task landed as a RED + GREEN pair on `firestarter_app/v1.7-shield-investigation`:

1. **Task 1 — MSG_INFO_HW + MSG_INFO_PHYSICAL_HW silkscreen branches (D-03 / WR-01)**
   - RED: `bd0b384` — `test(35-02): add failing tests for MSG_INFO_HW + MSG_INFO_PHYSICAL_HW silkscreen rendering`
   - GREEN: `a8240bd` — `feat(35-02): route MSG_INFO_HW + MSG_INFO_PHYSICAL_HW through _REVISION_SILKSCREEN (WR-01 close)`

2. **Task 2 — MSG_OK_CFG Override clause silkscreen rendering (D-04 / WR-02)**
   - RED: `947f808` — `test(35-02): update test_ok_cfg_p03_with_override_decodes for silkscreen rendering (D-04 RED)`
   - GREEN: `07d8daa` — `feat(35-02): route MSG_OK_CFG Override clause through _REVISION_SILKSCREEN (WR-02 close)`

3. **Task 3 — Full pytest verification + atomic-close** — no new commits; Task 1 + Task 2 TDD pairs collectively ARE the atomic plan-02 work on the sub-repo. The plan's original Task-3 instruction (one bundled `fix(35-02): ...` commit) was superseded by the per-task TDD commits required by `tdd="true"` on Tasks 1 + 2. The final pytest run reports `90 passed in 0.99s`, satisfying the Task 3 done criteria.

**Plan metadata commit:** owned by Plan 35-03 per `<sequential_execution>` directive (meta-repo submodule pointer bump deferred to Plan 03). Plan 35-02 produces sub-repo commits only.

_Note: This plan ran with `tdd="true"` on Tasks 1 + 2, so each task split into a `test(...)` RED commit and a `feat(...)` GREEN commit per the GSD TDD execution flow. Four sub-repo commits total instead of the plan's one-bundled-commit suggestion._

## Files Created/Modified

- `firestarter_app/firestarter/serial_comm.py` — Extended imports to bring in `MSG_INFO_HW` + `MSG_INFO_PHYSICAL_HW`; added two new branches in `_format_message` for those messages (single-u8 silkscreen lookup with `"HW: "` / `"Physical HW: "` prefix); replaced the raw `f"Rev{override}"` in the MSG_OK_CFG Override clause with `_REVISION_SILKSCREEN.get(override, f"Rev{override}")`; updated the function's docstring to describe the new branches and the D-04 override-clause change.
- `firestarter_app/tests/test_decoder.py` — Extended imports to bring in `MSG_INFO_HW` + `MSG_INFO_PHYSICAL_HW`; added 6 new tests (`test_info_hw_silkscreen_*` × 3 + `test_info_physical_hw_silkscreen_*` × 3) covering REVISION_1 / REVISION_UNKNOWN / unknown-byte fallback for both new branches; added `test_ok_cfg_p03_with_unknown_override_decodes` for the D-04 fallback path; flipped the existing `test_ok_cfg_p03_with_override_decodes` assertion from `"Rev2"` to `"Rev 2.0-class"`.

## Decisions Made

- **Frame-driven test shape, not direct-call** — Investigated whether INFO-severity frames flow through `Response` cleanly. They do (see existing `test_u24_render_as_hex_addr` at `tests/test_decoder.py:97-106` which asserts `response.type == "INFO"`). All 6 new MSG_INFO_HW / MSG_INFO_PHYSICAL_HW tests use the same `build_frame` + `_drive_one_response` shape as the existing MSG_OK_REV tests — no private-method testing needed, no test-shape divergence from the file's pattern.
- **Atomic-vs-bundled commit shape** — The plan's Task 3 instruction targeted ONE atomic `fix(35-02): ...` commit, but Tasks 1 + 2 carry `tdd="true"`, which under the GSD TDD execution flow requires RED then GREEN commits per task. The TDD shape won: 4 sub-repo commits (2 RED + 2 GREEN) instead of 1 bundled. Each commit cites the originating finding (WR-01 / WR-02) and decision (D-03 / D-04) so the per-finding git history is precise — better for future bisect.
- **D-04 fallback test added** — Beyond the plan's required test update, added `test_ok_cfg_p03_with_unknown_override_decodes` covering the `byte=0x99 → "Override HW: Rev153"` fallback path. Matches the same coverage pattern as Task 1's `test_info_hw_silkscreen_unknown_byte_falls_back` test — symmetric per-branch coverage.

## Deviations from Plan

None — plan executed exactly as written modulo two minor scope-additive choices documented under **Decisions Made**:

1. The Task 3 bundled-commit instruction was superseded by the `tdd="true"` per-task RED/GREEN commit requirement on Tasks 1 + 2 (this is the TDD execution flow's specified behavior, not a deviation from the plan's intent).
2. Added one optional test from the plan's `<action>` block — `test_ok_cfg_p03_with_unknown_override_decodes` — which the plan explicitly marked as "Recommended but not required". Test count is 7 new (within the plan's documented "6-8 new" range).

**Total deviations:** 0 auto-fixed (no Rule-1/2/3 fixes were needed; the substrate was clean).
**Impact on plan:** None — verification and success criteria met verbatim.

## Issues Encountered

- **Pre-existing test_ok_cfg_p03_with_unknown_override_decodes and test_info_hw_silkscreen_unknown_byte_falls_back coincidentally passed RED**: byte `0x99` formatted via the catalog `%u` already renders `Rev153` — identical to the fallback path. Only the REVISION_1 / REVISION_UNKNOWN tests actually failed RED. This is expected: the fallback case is shape-identical to the catalog default; the load-bearing tests are the silkscreen-named-byte cases. Documented in the RED commit messages.

- **Pre-existing operator WIP in `firestarter/config.py`** preserved as unstaged throughout — never touched, never staged, never committed. Final `git status` on `firestarter_app` shows `M firestarter/config.py` exactly as it was at execution start.

## User Setup Required

None — pure host-side code change. No environment variables, no dashboard configuration, no external service config.

## Next Phase Readiness

- **Plan 35-03 ready** — Plan 35-02 sub-repo work is complete on `firestarter_app/v1.7-shield-investigation`. Plan 35-03 owns the meta-repo submodule pointer bump that captures these 4 commits into the meta-repo's view.
- **Phase 35 Wave 2 ready** (once Plans 35-01 firmware fixes also land) — the host-side rendering is correct ahead of the operator-on-bench sideload session. UAT-1 / UAT-2 / UAT-3 will see consistent silkscreen strings across `MSG_OK_REV`, `MSG_OK_CFG`, `MSG_INFO_HW`, `MSG_INFO_PHYSICAL_HW` regardless of detect outcome.
- **No blockers introduced** — wire format invariant preserved per Phase 34 D-09; native tests bypass the new branches (host-side rendering is exclusive to the Python decoder); zero risk to firmware-side dispatch.

## Self-Check: PASSED

- `firestarter_app/firestarter/serial_comm.py` modified — FOUND (new MSG_INFO_HW + MSG_INFO_PHYSICAL_HW branches + MSG_OK_CFG override silkscreen lookup verified by `pytest tests/test_decoder.py -k 'info_hw_silkscreen or info_physical_hw or ok_cfg_p03'` → 9 passed)
- `firestarter_app/tests/test_decoder.py` modified — FOUND (7 new tests + 1 flipped assertion; full suite `pytest tests/` → 90 passed)
- Commit `bd0b384` (Task 1 RED) — FOUND (`git log --oneline | grep bd0b384` → match)
- Commit `a8240bd` (Task 1 GREEN) — FOUND
- Commit `947f808` (Task 2 RED) — FOUND
- Commit `07d8daa` (Task 2 GREEN) — FOUND
- Pre-existing operator WIP `firestarter/config.py` — UNSTAGED and untouched (`git status --short` → `M firestarter/config.py` exactly as at start)
- Meta-repo STATE.md, ROADMAP.md, submodule pointers — UNCHANGED (per `<sequential_execution>` directive)

---
*Phase: 35-documentation-milestone-close*
*Completed: 2026-05-25*

---
phase: 33
slug: silkscreen-label-code-alias-migration
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-25
---

# Phase 33 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Phase 33 is a name-only rename migration with GATE-1.7 byte-identical `.hex` non-regression as the load-bearing constraint (ALIAS-03).

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | PlatformIO + Unity (native test env) |
| **Framework (host)** | pytest 7.x |
| **Config file (firmware)** | `firestarter/platformio.ini` |
| **Config file (host)** | `firestarter_app/setup.py` (+ pytest defaults) |
| **Quick run command** | `cd firestarter && pio test -e native` (Unity) — fast subset |
| **Full suite command** | `cd firestarter && pio test -e native && cd ../firestarter_app && pytest` |
| **Build verification** | `cd firestarter && pio run -e uno && pio run -e uno328pb && pio run -e leonardo` |
| **GATE-1.7 byte-identical check** | `cmp <baseline>.hex <post-rename>.hex` per board (uno / uno328pb / leonardo) |
| **Estimated runtime** | ~120 seconds (build 3 envs ~60s + native test ~20s + pytest ~40s) |

---

## Sampling Rate

- **After every task commit:** Run `pio test -e native` (Unity) AND `cd firestarter_app && pytest` if Python touched
- **After every plan wave:** Run full suite + `pio run -e uno -e uno328pb -e leonardo` build + `cmp` against baseline `.hex` files captured pre-migration in Wave 0
- **Before `/gsd-verify-work`:** Full suite green AND all 3 `cmp`s succeed (or delta ≤ ~50 B per board documented in fix-commit) AND `grep -rn "VPE_ENABLE\|VPE_TO_VPP\|P1_VPP_ENABLE\|A9_VPP_ENABLE\|READ_WRITE\|REGULATOR" firestarter/include/ firestarter/src/` returns zero matches (excluding rurp_pinout.h legacy mapping if any)
- **Max feedback latency:** ~120 seconds full suite + build + `cmp`

---

## Per-Task Verification Map

> Filled by planner; planner assigns concrete task IDs after wave decomposition. Each rename task gets at minimum:
> 1. `pio test -e native` exit 0 (Unity assertions on canonical control-register values hold)
> 2. `grep -rn <old name>` in scoped files returns zero matches post-task
> 3. After wave: `pio run -e uno -e uno328pb -e leonardo` clean compile + `cmp` against baseline `.hex` (delta ≤ ~50 B per board)

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 33-00-01 | 00 (Wave 0) | 0 | infra | — | baseline `.hex` captured for all 3 boards | infra | `pio run -e uno && pio run -e uno328pb && pio run -e leonardo && cp .pio/build/*/firmware*.hex .planning/v1.7/phase-33-baseline-hex/` | ❌ W0 | ⬜ pending |
| 33-00-02 | 00 (Wave 0) | 0 | infra | — | check-migration script counts remaining old names | infra | `bash .planning/v1.7/phase-33-baseline-hex/check-migration.sh` | ❌ W0 | ⬜ pending |
| 33-XX-YY | per planner | per planner | ALIAS-01/02/03 | — | rename does not perturb behavior | unit + build + cmp | `pio test -e native && pio run -e uno && cmp .planning/v1.7/phase-33-baseline-hex/firestarter_uno.hex firestarter/.pio/build/uno/firestarter_uno.hex` | ⬜ planner-fills | ⬜ pending |

---

## Wave 0 Requirements

> Wave 0 is the pre-rename baseline-capture wave. It MUST run before any rename commit lands.

- [ ] `.planning/v1.7/phase-33-baseline-hex/` directory exists (gitignored per Phase 31 D-11 pattern)
- [ ] `.planning/v1.7/phase-33-baseline-hex/firestarter_uno.hex` captured from clean `pio run -e uno` on current `v1.7-shield-investigation` HEAD
- [ ] `.planning/v1.7/phase-33-baseline-hex/firestarter_uno328pb.hex` captured
- [ ] `.planning/v1.7/phase-33-baseline-hex/firestarter_leonardo.hex` captured
- [ ] `.planning/v1.7/phase-33-baseline-hex/check-migration.sh` exists — runs `grep -rn` for the 9-name old-alias set across `firestarter/include/` + `firestarter/src/` + `firestarter/test/`, prints remaining count per file, exit 1 if any remain after Wave 4 completes
- [ ] `.gitignore` excludes `.planning/v1.7/phase-33-baseline-hex/` (or honors existing `.planning/v1.7/` gitignore from Phase 31 D-11)
- [ ] Optional: `name_firmware.py` artifact-name verification (`firestarter_uno.hex` etc.) confirmed before rename starts

*Wave 0 is load-bearing for ALIAS-03 — without baseline `.hex` capture, GATE-1.7 byte-identical claim cannot be verified.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| §7 alias-table row count matches rename inventory | ALIAS-01 | Human readability — requires reading `.planning/v1.7-SHIELD-REVS.md` §7 and confirming each silkscreen label has exactly one row | Open `.planning/v1.7-SHIELD-REVS.md`, count §7 rows, confirm matches the 9 + R41 + A3 + JP4 + per-rev variants count from research §Exact Alias Inventory |
| Modified Rev 0 column carries `pending Phase 35` sentinels for rework cells | ALIAS-01 + D-09 | The set of rework-touched cells is operator-attested, not firmware-detected | Read §7 Modified Rev 0 column; verify sentinel pattern matches D-09 description |
| `name_firmware.py` artifact rename — if planner introduces new variant name | ALIAS-02 | Edge case if planner decides to rename `firestarter_<env>.hex` to `firestarter_<env>_v17.hex` (not expected, but possible) | Inspect `firestarter/tools/name_firmware.py` after Wave 4 |
| EEPROM `rurp_configuration_t` struct layout unchanged → `CONFIG_VERSION "VER06"` stays | implicit (no requirement bumps `CONFIG_VERSION`) | C++ struct layout is compile-time; verifying it didn't change requires reading the diff | After all rename commits, `git diff main..HEAD firestarter/include/rurp_shield.h` — confirm `rurp_configuration_t` struct body untouched and `CONFIG_VERSION "VER06"` line untouched |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers baseline-hex capture for all 3 AVR envs + check-migration script
- [ ] No watch-mode flags
- [ ] Feedback latency < ~120s (build + Unity + pytest)
- [ ] GATE-1.7 `.hex` `cmp` passes (or documented delta ≤ ~50 B per board) for uno / uno328pb / leonardo
- [ ] `grep -rn` for old 9-name alias set in `firestarter/include/` + `firestarter/src/` returns zero matches after Wave 4
- [ ] §7 row count matches alias inventory (manual check)
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

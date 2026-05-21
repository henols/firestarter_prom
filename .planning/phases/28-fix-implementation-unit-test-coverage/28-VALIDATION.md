---
phase: 28
slug: fix-implementation-unit-test-coverage
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-21
---

# Phase 28 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Source: `28-RESEARCH.md` §"Validation Architecture".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | PlatformIO 6.x + Unity 2.x + ArduinoFake 0.4.x |
| **Config file** | `firestarter/platformio.ini` `[env:native]` (lines 67-102) |
| **Quick run command** | `cd /workspaces/firestarter && pio test -e native -f "*test_data_input*"` |
| **Full suite command** | `cd /workspaces/firestarter && pio test -e native` |
| **Production build smoke** | `cd /workspaces/firestarter && pio run -e uno && pio run -e leonardo && pio run -e uno328pb` |
| **Estimated runtime** | ~30 s (quick) / ~90 s (full suite + 3-board build) |

---

## Sampling Rate

- **After every task commit (Wave A test scaffold):** Run `pio test -e native -f "*test_data_input*"` — expect RED bar with `test_rurp_set_data_input_clears_data_pullups_leonardo:FAIL` AND `test_rurp_read_data_buffer_reassembles_data_bus:PASS`.
- **After every task commit (Wave B Commit 1 — PORTx-clear):** Run `pio test -e native -f "*test_data_input*"` — expect GREEN on both Unity cases.
- **After every task commit (Wave B Commit 2 — `_NOP()` settling):** Run `pio test -e native -f "*test_data_input*"` — still GREEN; PLUS production-build smoke for all 3 envs.
- **After every plan wave:** Run `pio test -e native` (full native suite) — no regressions in `test_dispatch` / `test_messages`.
- **Before `/gsd-verify-work`:** Full suite must be green AND `.planning/v1.6-EVIDENCE.md` `## Phase 28 — Fix Commit References` section populated per D-08.
- **Max feedback latency:** ~30 seconds per task; ~90 seconds per wave.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 28-01-01 | 01 | A | FIX-02 | — | Branch cut from `beta@bc0f5ac`; no behavior change | git inspection | `cd /workspaces/firestarter && git rev-parse v1.6-read-bug` exits 0 | ❌ W0 | ⬜ pending |
| 28-01-02 | 01 | A | FIX-02 | — | Unity test scaffolded (RED bar) | unit | `pio test -e native -f "*test_data_input*"` exits non-zero with `test_rurp_set_data_input_clears_data_pullups_leonardo:FAIL` | ❌ W0 | ⬜ pending |
| 28-01-03 | 01 | A | FIX-02 | — | `test_filter` extended; native + 3 prod builds clean | unit + build | `pio test -e native` + `pio run -e {uno,leonardo,uno328pb}` all exit 0 | ❌ W0 | ⬜ pending |
| 28-02-01 | 02 | B | FIX-01 | — | Commit 1 — PORTx-clear lands; Unity test GREEN | unit + git | `pio test -e native -f "*test_data_input*"` exits 0 AND `git log --grep="PORTD/PORTC/PORTE pullups"` shows 1 commit with `RCA:` footer | (Wave A) | ⬜ pending |
| 28-02-02 | 02 | B | FIX-01 | — | Commit 2 — `_NOP()` settling lands; Unity test stays GREEN | unit + git | `pio test -e native -f "*test_data_input*"` exits 0 AND `git log --grep="settling delay"` shows 1 commit with `RCA:` footer | (Wave A) | ⬜ pending |
| 28-02-03 | 02 | B | FIX-03 (desk-side) | — | Read-path-only diff confirmed | manual + git | `git diff bc0f5ac..HEAD -- src/boards/leonardo_rurp_shield.cpp` only modifies `rurp_set_data_input` + `rurp_read_data_buffer` | (Wave A) | ⬜ pending |
| 28-02-04 | 02 | B | ROADMAP SC#4 | — | Per-board hex sizes captured; Δ within ±200 B | build + size | `pio run -e {uno,leonardo,uno328pb}` + size capture; recorded in Wave B Commit 2 message | (Wave A) | ⬜ pending |
| 28-02-05 | 02 | B | FIX-01 | — | EVIDENCE.md appended with `## Phase 28 — Fix Commit References` | doc + grep | `grep "## Phase 28 — Fix Commit References" .planning/v1.6-EVIDENCE.md` exits 0 with SHAs + sizes table | n/a | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `firestarter/test/native/avr/test_data_input/test_rurp_set_data_input.cpp` — Unity test file with two RUN_TEST cases (covers FIX-02 RED→GREEN)
- [ ] `firestarter/test/native/avr/test_data_input/host_stubs.cpp` — minimal host stubs (Serial_::operator bool per Q6)
- [ ] `firestarter/test/native/avr/test_data_input/avr/pgmspace.h` — host shim mirror of `test_dispatch/avr/pgmspace.h`
- [ ] `firestarter/platformio.ini` line 80 area — add `native/avr/test_data_input` to `[env:native].test_filter`

*Framework install: NONE needed — PIO + Unity + ArduinoFake already present in `[env:native]`.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GATE-1.6 byte-for-byte bench verify (`firestarter write` + `dev read -s N` on W27C512 or SST27SF512) | FIX-03 | Requires real silicon + bench fixture; bench-gated per ROADMAP SC#3 | DEFERRED — Phase 29 owns end-to-end bench validation. Phase 28 only does desk-side read-path-only diff inspection (covered by automated `git diff` check). |
| Read-path-only diff confirmation | FIX-03 desk-side | Cross-checking which functions are modified vs the GATE-1.6 contract | `cd /workspaces/firestarter && git diff bc0f5ac..HEAD -- src/boards/leonardo_rurp_shield.cpp` — visually confirm only `rurp_set_data_input` + `rurp_read_data_buffer` hunks; recorded in Wave B verifier block |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies (one manual-only verify is deferred to Phase 29)
- [ ] Sampling continuity: every task in Wave A and Wave B runs `pio test -e native -f "*test_data_input*"` post-commit — no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (3 new files in `test_data_input/` + 1 `platformio.ini` line)
- [ ] No watch-mode flags (`pio test` is one-shot)
- [ ] Feedback latency < 30s per task (Unity native suite is sub-second; PIO startup ~10-20s)
- [ ] `nyquist_compliant: true` set in frontmatter after planner adds task IDs

**Approval:** pending

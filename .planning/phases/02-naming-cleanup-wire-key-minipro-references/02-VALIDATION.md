---
phase: 02
slug: naming-cleanup-wire-key-minipro-references
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-05-12
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Derived from `02-RESEARCH.md` §"Validation Architecture".

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework (firmware)** | PlatformIO + Unity (`pio test -e native`) |
| **Framework (Python)** | None established — `check_dispatch.py` (stdlib static scan) + CLI smoke is the contract |
| **Config file (firmware)** | `firestarter/platformio.ini` `[env:native]` |
| **Config file (Python)** | — |
| **Quick run command** | `cd firestarter_app && python tools/check_dispatch.py` (~1s; 743-chip iteration) |
| **Full suite command** | `cd firestarter_app && python tools/check_dispatch.py && firestarter --help && firestarter info W27C512 && firestarter info --adapter W27C512` plus `cd firestarter && pio test -e native` |
| **Estimated runtime** | Python ≈3s; firmware native ≈15-20s |

---

## Sampling Rate

- **After every task commit:** Run `cd firestarter_app && python tools/check_dispatch.py` (Python-side changes) OR `cd firestarter && pio test -e native` (firmware-side changes).
- **After every plan wave:** Run the full Python smoke + firmware native test suite.
- **Before `/gsd-verify-work`:** Full suite must be green AND all three CLAUDE.md files manually reviewed for consistency.
- **Max feedback latency:** ~25s (Python ≈3s + firmware native ≈20s).

---

## Per-Task Verification Map

> Task IDs are placeholders — gsd-planner will replace them with the actual `{N}-{plan}-{task}` IDs after plan creation. The map below describes WHAT must be verified per requirement, not yet WHICH task does it.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-XX | 01 | 1 | WIRE-01 (Python emit) | T-02-01 (stale-wire over-voltage) | Python emits ONLY `"vpp_mv"`; SAF-04 traps stale-key partial upgrade | static scan | `python tools/check_dispatch.py` | ✅ existing | ⬜ pending |
| 02-01-XX | 01 | 1 | WIRE-01 (firmware parse) | T-02-01 | Firmware parses `"vpp_mv"` into `handle->vpp_mv`; compile-clean | compile | `cd firestarter && pio run -e uno && pio run -e leonardo` | ✅ existing | ⬜ pending |
| 02-01-XX | 01 | 1 | WIRE-01 (doc) | — | CLAUDE.md wire example shows only `"vpp_mv"` | grep | `! grep -F '"vpp":' firestarter_app/CLAUDE.md` | ✅ existing | ⬜ pending |
| 02-02-XX | 02 | 1 | CLEAN-01 (rename atomicity) | — | Zero remaining references to `minipro_complete_db.json` | grep | `! grep -rn 'minipro_complete_db' firestarter_app/ firestarter/ CLAUDE.md` | ✅ existing | ⬜ pending |
| 02-02-XX | 02 | 1 | CLEAN-01 (package data) | — | `pyproject.toml`+`MANIFEST.in` reference the new filename; wheel build succeeds | smoke | `cd firestarter_app && pip install -e . && firestarter info W27C512` | ✅ existing | ⬜ pending |
| 02-02-XX | 02 | 1 | WIRE-01 internal (`vpp_volts`) | — | `_map_data()` output uses `"vpp_volts"`; downstream consumers (`eprom_info.py:271`, `ic_layout.py:516`) updated | static scan | `python tools/check_dispatch.py` (via `db.convert_to_programmer` round-trip in Shape A) | ✅ existing | ⬜ pending |
| 02-03-XX | 03 | 2 | WIRE-02 (regression scan) | T-02-01 | `check_dispatch.py` asserts `"vpp_mv" in wire ∧ "vpp" ∉ wire` for all 743 chips | static scan | `python tools/check_dispatch.py` | ✅ existing (augmented in Plan 02-03) | ⬜ pending |
| 02-03-XX | 03 | 2 | CLEAN-02 (firmware mentions = 0) | — | No `minipro` mentions in `firestarter/` sub-repo | grep | `! grep -rin minipro firestarter/CLAUDE.md firestarter/src/ firestarter/include/` | ✅ existing | ⬜ pending |
| 02-03-XX | 03 | 2 | CLEAN-02 (host mentions ≤ 2) | — | Exactly 1 attribution line in `firestarter_app/CLAUDE.md` + `MINIPRO_XML_URL` constant comment | grep + count | `grep -cin minipro firestarter_app/CLAUDE.md` ≤ 1; `grep -cin minipro firestarter_app/firestarter/database.py firestarter_app/tools/check_dispatch.py` = 0 | ✅ existing | ⬜ pending |
| 02-03-XX | 03 | 2 | SC#5 CLI smoke | — | `firestarter info W27C512` resolves the renamed DB | CLI smoke | `cd firestarter_app && firestarter --help && firestarter info W27C512 && firestarter info --adapter W27C512` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

**Existing infrastructure covers all phase requirements.** Phase 2 reuses:

- `firestarter_app/tools/check_dispatch.py` (regression scanner — augmented in Plan 02-03 with two new asserts inside the existing 743-chip iteration; no new test file).
- `firestarter/test/native/avr/test_dispatch/` (PlatformIO native dispatch tests — already cover the post-parse `configure_*` handlers).
- `firestarter` CLI (smoke target — already installed via `pip install -e .` in the dev env).

No new test framework, fixtures, or stub files needed.

**Identified gap (DEFERRED):** Phase 2 leaves a pre-existing v1.0 gap intact — `json_parser.c` has no native PlatformIO test. The atomic-flip three-line edit is small enough that careful code review + `check_dispatch.py` Shape A round-trip + Phase 4 hardware verification are sufficient. Native parser tests are tracked as a v1.2 hardening candidate (see RESEARCH.md §"Wave 0 Gaps"); not in Phase 2 scope.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Three-CLAUDE.md consistency (meta + 2 sub-repo) | CLEAN-01 / CLEAN-02 | No automated tool checks cross-doc semantic consistency (filename + attribution line counts can be greped, but reading flow + wording cannot) | At phase close, open meta `CLAUDE.md`, `firestarter_app/CLAUDE.md`, `firestarter/CLAUDE.md` side-by-side; confirm: (1) all three use `chip_database.json`; (2) `firestarter_app/CLAUDE.md` has exactly one attribution line; (3) `firestarter/CLAUDE.md` has zero `minipro` mentions; (4) wire-JSON example in `firestarter_app/CLAUDE.md` shows only `"vpp_mv"`. |
| Real hardware end-to-end (Uno + Leonardo with RURP shield) | WIRE-01 + CLEAN-01 | Requires Arduino board + RURP shield — not available in devcontainer | **Deferred to Phase 4 / HW-* tasks** per Phase 2 CONTEXT.md "Out of scope". `check_dispatch.py` simulator paths cover the static contract; Phase 4 owns physical-write validation. |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (none — existing infra covers everything)
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter after gsd-planner fills in real task IDs

**Approval:** pending (gsd-planner to refine task IDs; gsd-plan-checker to verify)
